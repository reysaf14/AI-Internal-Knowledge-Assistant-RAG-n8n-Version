-- =============================================================================
-- Asisten Pengetahuan Internal Toko Makmur Jaya — PostgreSQL Initialization
-- Architecture version: 1.2 | Environment Schema version: 1.1
-- =============================================================================
-- This script initializes the database for both local-isolated and demo-vps profiles.
-- It creates schemas, roles, grants, and RAG tables.
-- Run ONCE during initial deployment (before n8n starts).
-- Idempotent: uses IF NOT EXISTS / DO blocks where appropriate.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. SCHEMAS
-- -----------------------------------------------------------------------------
-- n8n schema: owned by n8n application role, used only by n8n for workflow,
-- credentials (encrypted), and instance metadata
CREATE SCHEMA IF NOT EXISTS n8n AUTHORIZATION n8n_app;

-- rag schema: corpus/vector/operational state, separate from n8n internals
CREATE SCHEMA IF NOT EXISTS rag AUTHORIZATION rag_ingest;

-- -----------------------------------------------------------------------------
-- 2. ROLES (Created by bootstrap; passwords set via environment variables)
-- -----------------------------------------------------------------------------
-- Role: n8n_app (least-privilege for n8n schema)
-- Created by bootstrap with password from N8N_DB_PASSWORD
-- GRANT USAGE ON SCHEMA n8n TO n8n_app; (already owner via AUTHORIZATION)
-- GRANT CREATE, USAGE ON SCHEMA n8n TO n8n_app; (owner has all)

-- Role: rag_ingest (write staging, validate, activate, cleanup corpus)
-- Created by bootstrap with password from RAG_INGEST_DB_PASSWORD
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rag_ingest') THEN
        CREATE ROLE rag_ingest WITH LOGIN PASSWORD 'RAG_INGEST_DB_PASSWORD_PLACEHOLDER';
    END IF;
END
$$;

-- Role: rag_runtime (read corpus/settings + write dedup/safe events only)
-- Created by bootstrap with password from RAG_RUNTIME_DB_PASSWORD
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rag_runtime') THEN
        CREATE ROLE rag_runtime WITH LOGIN PASSWORD 'RAG_RUNTIME_DB_PASSWORD_PLACEHOLDER';
    END IF;
END
$$;

-- -----------------------------------------------------------------------------
-- 3. GRANTS
-- -----------------------------------------------------------------------------
-- rag_ingest: full control over rag schema (DDL + DML for ingestion pipeline)
GRANT USAGE, CREATE ON SCHEMA rag TO rag_ingest;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA rag TO rag_ingest;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA rag TO rag_ingest;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT ALL ON TABLES TO rag_ingest;
ALTER DEFAULT PRIVILEGES IN SCHEMA rag GRANT ALL ON SEQUENCES TO rag_ingest;

-- rag_runtime: read-only on corpus/settings + limited write on operational tables
GRANT USAGE ON SCHEMA rag TO rag_runtime;
GRANT SELECT ON ALL TABLES IN SCHEMA rag TO rag_runtime;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA rag TO rag_runtime;
-- Explicit write grants for operational tables (telegram_updates, safe_events)
-- Applied after table creation below

-- n8n_app: no access to rag schema (strict separation)
REVOKE ALL ON SCHEMA rag FROM n8n_app;

-- -----------------------------------------------------------------------------
-- 4. RAG TABLES
-- -----------------------------------------------------------------------------
-- All tables in rag schema. Primary keys use UUID for correlation IDs where needed.
-- Timestamps use timestamptz for timezone awareness.

-- 4.1 rag_settings — Runtime configuration (single row, versioned by config_revision)
CREATE TABLE IF NOT EXISTS rag.rag_settings (
    id                          BIGINT PRIMARY KEY DEFAULT 1,  -- singleton row
    config_revision             TEXT NOT NULL,                 -- e.g., "2026-09-14-v1"
    chat_model                  TEXT,                          -- provider:model-id@version
    embedding_model             TEXT,                          -- provider:model-id@version
    embedding_profile_id        TEXT,                          -- hash of embedding_model + norm + dim
    embedding_dimension         INTEGER,                       -- must match embedding_profile_id
    retrieval_limit             INTEGER DEFAULT 5,
    minimum_similarity          REAL DEFAULT 0.75,
    context_bound               INTEGER DEFAULT 3000,          -- max chars/tokens to model
    output_bound                INTEGER DEFAULT 500,           -- max response tokens
    active_corpus_version       TEXT,                          -- corpus_version hash
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT rag_settings_singleton CHECK (id = 1)
);

-- 4.2 corpus_versions — Versioned corpus metadata (one active at a time)
CREATE TABLE IF NOT EXISTS rag.corpus_versions (
    corpus_version              TEXT PRIMARY KEY,              -- manifest hash
    status                      TEXT NOT NULL CHECK (status IN ('staging', 'active', 'failed', 'superseded')),
    document_count              INTEGER NOT NULL DEFAULT 0,
    chunk_count                 INTEGER NOT NULL DEFAULT 0,
    embedding_profile_id        TEXT NOT NULL,                 -- must match rag_settings at activation
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at                TIMESTAMPTZ,
    failed_at                   TIMESTAMPTZ,
    failure_reason              TEXT
);

-- Index for finding active version quickly
CREATE INDEX IF NOT EXISTS idx_corpus_versions_active
    ON rag.corpus_versions (status) WHERE status = 'active';

-- 4.3 documents — Vector store chunks (one row per chunk)
CREATE TABLE IF NOT EXISTS rag.documents (
    id                          BIGSERIAL PRIMARY KEY,
    corpus_version              TEXT NOT NULL REFERENCES rag.corpus_versions(corpus_version) ON DELETE CASCADE,
    source_name                 TEXT NOT NULL,                 -- e.g., "01_SOP_Buka_Toko.md"
    source_hash                 TEXT NOT NULL,                 -- SHA-256 of file content
    chunk_index                 INTEGER NOT NULL,              -- 0-based index within document
    content                     TEXT NOT NULL,                 -- chunk text content
    embedding                   VECTOR,                        -- pgvector column (dimension set at init)
    metadata                    JSONB NOT NULL DEFAULT '{}',   -- extensible metadata
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Unique per corpus version + source + chunk
    CONSTRAINT uq_doc_chunk UNIQUE (corpus_version, source_hash, chunk_index)
);

-- Vector index (HNSW) — created after pgvector extension is available
-- CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw
--     ON rag.documents USING hnsw (embedding vector_cos_ops)
--     WITH (m = 16, ef_construction = 64);

-- Filter index for active corpus queries
CREATE INDEX IF NOT EXISTS idx_documents_corpus_version
    ON rag.documents (corpus_version);

-- 4.4 telegram_updates — Deduplication & delivery tracking (no payload)
CREATE TABLE IF NOT EXISTS rag.telegram_updates (
    id                          BIGSERIAL PRIMARY KEY,
    bot_scope_hash              TEXT NOT NULL,                 -- hash(bot_token) — non-reversible
    update_id                   BIGINT NOT NULL,               -- Telegram update_id
    status                      TEXT NOT NULL CHECK (status IN ('claimed', 'processing', 'delivered', 'failed', 'delivery_unknown')),
    claimed_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    processing_started_at       TIMESTAMPTZ,
    delivery_attempted_at       TIMESTAMPTZ,
    delivery_succeeded_at       TIMESTAMPTZ,
    error_category              TEXT,                          -- safe category only (timeout, auth, rate_limit, validation, etc.)
    config_revision             TEXT,                          -- rag_settings.config_revision at processing time
    corpus_version              TEXT,                          -- active corpus_version at processing time
    -- Unique dedup key: bot_scope_hash + update_id
    CONSTRAINT uq_telegram_update UNIQUE (bot_scope_hash, update_id)
);

CREATE INDEX IF NOT EXISTS idx_telegram_updates_status
    ON rag.telegram_updates (status);

-- 4.5 safe_events — Sanitized operational events (no payload, no PII)
CREATE TABLE IF NOT EXISTS rag.safe_events (
    id                          BIGSERIAL PRIMARY KEY,
    correlation_id              TEXT NOT NULL,                 -- non-reversible hash
    workflow                    TEXT NOT NULL,                 -- 'ingestion' | 'qa'
    stage                       TEXT NOT NULL,                 -- e.g., 'retrieval', 'embedding', 'generation', 'send'
    status                      TEXT NOT NULL CHECK (status IN ('started', 'success', 'failed', 'timeout', 'aborted')),
    duration_ms                 INTEGER,                       -- stage duration
    error_category              TEXT,                          -- safe category only
    config_revision             TEXT,                          -- rag_settings.config_revision
    corpus_version              TEXT,                          -- active corpus_version (if applicable)
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_safe_events_correlation
    ON rag.safe_events (correlation_id);

CREATE INDEX IF NOT EXISTS idx_safe_events_created_at
    ON rag.safe_events (created_at);

-- -----------------------------------------------------------------------------
-- 5. RAG_RUNTIME SPECIFIC WRITE GRANTS (after tables exist)
-- -----------------------------------------------------------------------------
-- telegram_updates: INSERT + UPDATE (status transitions only)
GRANT INSERT, UPDATE (status, processing_started_at, delivery_attempted_at, delivery_succeeded_at, error_category, config_revision, corpus_version)
    ON rag.telegram_updates TO rag_runtime;
GRANT USAGE, SELECT ON SEQUENCE rag.telegram_updates_id_seq TO rag_runtime;

-- safe_events: INSERT only
GRANT INSERT ON rag.safe_events TO rag_runtime;
GRANT USAGE, SELECT ON SEQUENCE rag.safe_events_id_seq TO rag_runtime;

-- documents: SELECT only (already granted via SELECT ALL TABLES)
-- corpus_versions: SELECT only
-- rag_settings: SELECT only

-- -----------------------------------------------------------------------------
-- 6. INITIAL RAG_SETTINGS ROW (placeholder — Engineer fills after calibration)
-- -----------------------------------------------------------------------------
INSERT INTO rag.rag_settings (id, config_revision)
VALUES (1, 'UNINITIALIZED')
ON CONFLICT (id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- 7. PGVECTOR EXTENSION (required for VECTOR column)
-- -----------------------------------------------------------------------------
-- This must be run as superuser (bootstrap role) before tables with VECTOR type.
-- Included here for completeness; actual execution depends on deployment order.
-- CREATE EXTENSION IF NOT EXISTS vector;

-- Note: Vector index (HNSW) on documents.embedding should be created AFTER
-- embedding_dimension is known and pgvector extension is installed.
-- Example (run after RAG_EMBEDDING_DIMENSION is set and data loaded):
-- CREATE INDEX idx_documents_embedding_hnsw ON rag.documents USING hnsw (embedding vector_cos_ops);