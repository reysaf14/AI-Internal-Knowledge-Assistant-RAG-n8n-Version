#!/usr/bin/env bash
# =============================================================================
# Asisten Pengetahuan Internal Toko Makmur Jaya — DB initialization
# Architecture version: 1.2 | Environment Schema version: 1.1
# =============================================================================
# This script runs via docker-entrypoint-initdb.d (shell scripts run with env
# vars available). It creates schemas, roles, grants, and RAG tables.
# Idempotent: uses IF NOT EXISTS / DO blocks.
# =============================================================================
set -euo pipefail

echo "[db-init] Starting database initialization..."

# -----------------------------------------------------------------------------
# 1. EXTENSION (must be first — superuser bootstrap owns this phase)
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'EOSQL'
CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

echo "[db-init] pgvector extension created."

# -----------------------------------------------------------------------------
# 2. ROLES (created BEFORE schemas; passwords from container env vars)
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'n8n_app') THEN
        CREATE ROLE n8n_app LOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_ingest') THEN
        CREATE ROLE rag_ingest LOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_runtime') THEN
        CREATE ROLE rag_runtime LOGIN;
    END IF;
END
\$\$;

ALTER ROLE n8n_app WITH PASSWORD '${N8N_DB_PASSWORD}';
ALTER ROLE rag_ingest WITH PASSWORD '${RAG_INGEST_DB_PASSWORD}';
ALTER ROLE rag_runtime WITH PASSWORD '${RAG_RUNTIME_DB_PASSWORD}';
EOSQL

echo "[db-init] Roles created."

# -----------------------------------------------------------------------------
# 4. DATABASE-LEVEL GRANTS (CONNECT + CREATE for schema creation)
# -----------------------------------------------------------------------------
# n8n_app needs CONNECT to the database + CREATE to create its schema tables
# rag_ingest needs CONNECT + CREATE to create tables in rag schema
# rag_runtime needs CONNECT for read access
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOSQL
GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO n8n_app;
GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO rag_ingest;
GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO rag_runtime;
GRANT CREATE ON DATABASE "$POSTGRES_DB" TO n8n_app;
GRANT CREATE ON DATABASE "$POSTGRES_DB" TO rag_ingest;
EOSQL

echo "[db-init] Database-level grants configured."

# -----------------------------------------------------------------------------
# 5. SCHEMAS (roles now exist + have DB-level CREATE)
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'EOSQL'
CREATE SCHEMA IF NOT EXISTS n8n AUTHORIZATION n8n_app;
CREATE SCHEMA IF NOT EXISTS rag AUTHORIZATION rag_ingest;
EOSQL

echo "[db-init] Schemas created."

# -----------------------------------------------------------------------------
# 6. GRANTS (separation: n8n_app only n8n, rag roles only rag)
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'EOSQL'
-- n8n schema: full control for n8n_app (owner via AUTHORIZATION)
GRANT ALL ON SCHEMA n8n TO n8n_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA n8n GRANT ALL ON TABLES TO n8n_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA n8n GRANT ALL ON SEQUENCES TO n8n_app;

-- rag schema: ingest has full control; runtime read-only + limited write
GRANT USAGE, CREATE ON SCHEMA rag TO rag_ingest;
GRANT USAGE ON SCHEMA rag TO rag_runtime;
-- Runtime SELECT on CURRENT tables (created later in this script — applies to existing at this point)
-- and DEFAULT privileges for FUTURE tables (must exist so runtime can read new tables)
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT SELECT ON TABLES TO rag_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT SELECT ON SEQUENCES TO rag_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT ALL ON TABLES TO rag_ingest;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT ALL ON SEQUENCES TO rag_ingest;

-- n8n_app: no access to rag schema (strict separation)
REVOKE ALL ON SCHEMA rag FROM n8n_app;
EOSQL

echo "[db-init] Grants configured."

# -----------------------------------------------------------------------------
# 7. RAG TABLES
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'EOSQL'
-- 4.1 rag_settings — singleton runtime config row; values filled after calibration
CREATE TABLE IF NOT EXISTS rag.rag_settings (
    id                          BIGINT PRIMARY KEY DEFAULT 1,
    config_revision             TEXT NOT NULL,
    chat_base_url               TEXT,
    chat_api_path               TEXT DEFAULT '/chat/completions',
    chat_model                  TEXT,
    embedding_model             TEXT,
    embedding_profile_id        TEXT,
    embedding_dimension         INTEGER,
    retrieval_limit             INTEGER DEFAULT 5,
    minimum_similarity          REAL DEFAULT 0.75,
    context_bound               INTEGER DEFAULT 3000,
    output_bound                INTEGER DEFAULT 500,
    ai_timeout_max              INTEGER,
    ingest_timeout_max          INTEGER,
    telegram_allowed_chat_id    TEXT,
    active_corpus_version       TEXT,
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT rag_settings_singleton CHECK (id = 1)
);

-- 4.2 corpus_versions — one active version at a time
CREATE TABLE IF NOT EXISTS rag.corpus_versions (
    corpus_version              TEXT PRIMARY KEY,
    status                      TEXT NOT NULL CHECK (status IN ('staging', 'active', 'failed', 'superseded')),
    document_count              INTEGER NOT NULL DEFAULT 0,
    chunk_count                 INTEGER NOT NULL DEFAULT 0,
    embedding_profile_id        TEXT NOT NULL,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at                TIMESTAMPTZ,
    failed_at                   TIMESTAMPTZ,
    failure_reason              TEXT
);

CREATE INDEX IF NOT EXISTS idx_corpus_versions_active
    ON rag.corpus_versions (status) WHERE status = 'active';

-- 4.3 documents — vector store chunks (embedding VECTOR dimension added after calibration)
CREATE TABLE IF NOT EXISTS rag.documents (
    id                          BIGSERIAL PRIMARY KEY,
    corpus_version              TEXT NOT NULL REFERENCES rag.corpus_versions(corpus_version) ON DELETE CASCADE,
    source_name                 TEXT NOT NULL,
    source_hash                 TEXT NOT NULL,
    chunk_index                 INTEGER NOT NULL,
    content                     TEXT NOT NULL,
    embedding                   VECTOR,
    embedding_profile_id        TEXT NOT NULL,
    metadata                    JSONB NOT NULL DEFAULT '{}',
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_doc_chunk UNIQUE (corpus_version, source_hash, chunk_index)
);

CREATE INDEX IF NOT EXISTS idx_documents_corpus_version
    ON rag.documents (corpus_version);

CREATE INDEX IF NOT EXISTS idx_documents_profile
    ON rag.documents (corpus_version, embedding_profile_id);

-- 4.4 telegram_updates — dedup & delivery tracking, no payload
CREATE TABLE IF NOT EXISTS rag.telegram_updates (
    id                          BIGSERIAL PRIMARY KEY,
    bot_scope_hash              TEXT NOT NULL,
    update_id                   BIGINT NOT NULL,
    status                      TEXT NOT NULL CHECK (status IN ('claimed', 'processing', 'delivered', 'failed', 'delivery_unknown')),
    claimed_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_started_at       TIMESTAMPTZ,
    delivery_attempted_at       TIMESTAMPTZ,
    delivery_succeeded_at       TIMESTAMPTZ,
    error_category              TEXT,
    config_revision             TEXT,
    corpus_version              TEXT,
    CONSTRAINT uq_telegram_update UNIQUE (bot_scope_hash, update_id)
);

CREATE INDEX IF NOT EXISTS idx_telegram_updates_status
    ON rag.telegram_updates (status);

-- 4.5 safe_events — sanitized operational events, no payload/PII
CREATE TABLE IF NOT EXISTS rag.safe_events (
    id                          BIGSERIAL PRIMARY KEY,
    correlation_id              TEXT NOT NULL,
    workflow                    TEXT NOT NULL,
    stage                       TEXT NOT NULL,
    status                      TEXT NOT NULL CHECK (status IN ('started', 'success', 'failed', 'timeout', 'aborted')),
    duration_ms                 INTEGER,
    error_category              TEXT,
    config_revision             TEXT,
    corpus_version              TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_safe_events_correlation
    ON rag.safe_events (correlation_id);

CREATE INDEX IF NOT EXISTS idx_safe_events_created_at
    ON rag.safe_events (created_at);

-- Initial settings row (placeholder; Engineer fills after calibration)
INSERT INTO rag.rag_settings (id, config_revision)
VALUES (1, 'UNINITIALIZED')
ON CONFLICT (id) DO NOTHING;
EOSQL

# -----------------------------------------------------------------------------
# 8. RAG_RUNTIME SPECIFIC WRITE GRANTS (after tables exist)
# -----------------------------------------------------------------------------
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'EOSQL'
-- Runtime SELECT on all CURRENT tables (idempotent re-run safety)
GRANT SELECT ON ALL TABLES IN SCHEMA rag TO rag_runtime;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA rag TO rag_runtime;

-- Ingest write on all CURRENT tables (idempotent re-run safety)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA rag TO rag_ingest;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA rag TO rag_ingest;

-- Runtime-specific write grants on operational tables only
GRANT INSERT, UPDATE (status, processing_started_at, delivery_attempted_at, delivery_succeeded_at, error_category, config_revision, corpus_version)
    ON rag.telegram_updates TO rag_runtime;
GRANT USAGE, SELECT ON SEQUENCE rag.telegram_updates_id_seq TO rag_runtime;

GRANT INSERT ON rag.safe_events TO rag_runtime;
GRANT USAGE, SELECT ON SEQUENCE rag.safe_events_id_seq TO rag_runtime;
EOSQL

echo "[db-init] Database initialization complete."
