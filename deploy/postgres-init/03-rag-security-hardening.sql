-- =============================================================================
-- RAG least-privilege hardening for fresh and existing volumes.
-- Run as the PostgreSQL bootstrap/maintenance owner after 01-init.sh and
-- 02-rag-schema-alignment.sql. No application role receives DDL or settings
-- mutation authority. The activation function is the only ingest-side
-- transition that changes the active corpus pointer.
-- =============================================================================

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'rag_owner') THEN
        CREATE ROLE rag_owner NOLOGIN;
    END IF;
END
$$;

DO $$
BEGIN
    EXECUTE format('REVOKE CREATE ON DATABASE %I FROM rag_ingest, rag_runtime', current_database());
END
$$;
ALTER SCHEMA rag OWNER TO rag_owner;

ALTER TABLE rag.rag_settings OWNER TO rag_owner;
ALTER TABLE rag.corpus_versions OWNER TO rag_owner;
ALTER TABLE rag.documents OWNER TO rag_owner;
ALTER TABLE rag.telegram_updates OWNER TO rag_owner;
ALTER TABLE rag.safe_events OWNER TO rag_owner;

ALTER SEQUENCE rag.documents_id_seq OWNER TO rag_owner;
ALTER SEQUENCE rag.telegram_updates_id_seq OWNER TO rag_owner;
ALTER SEQUENCE rag.safe_events_id_seq OWNER TO rag_owner;

REVOKE CREATE ON SCHEMA rag FROM rag_ingest, rag_runtime, PUBLIC;
GRANT USAGE ON SCHEMA rag TO rag_ingest, rag_runtime;

REVOKE ALL ON ALL TABLES IN SCHEMA rag FROM rag_ingest, rag_runtime, PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA rag FROM rag_ingest, rag_runtime, PUBLIC;

-- Ingestion receives settings only. Candidate creation, staging writes,
-- evidence counts, and failure marking are SECURITY DEFINER procedures below;
-- rag_ingest cannot read document content or mutate corpus tables directly.
GRANT SELECT ON rag.rag_settings TO rag_ingest;

-- Runtime: corpus/settings reads plus the two operational write surfaces.
GRANT SELECT ON rag.rag_settings, rag.corpus_versions, rag.documents TO rag_runtime;
GRANT SELECT, UPDATE (status, processing_started_at, delivery_attempted_at,
    delivery_succeeded_at, error_category, config_revision, corpus_version)
    ON rag.telegram_updates TO rag_runtime;
GRANT INSERT (bot_scope_hash, update_id, status, processing_started_at, config_revision, corpus_version)
    ON rag.telegram_updates TO rag_runtime;
GRANT USAGE ON SEQUENCE rag.telegram_updates_id_seq TO rag_runtime;
GRANT INSERT (correlation_id, workflow, stage, status, duration_ms, error_category,
    config_revision, corpus_version) ON rag.safe_events TO rag_runtime;
GRANT USAGE ON SEQUENCE rag.safe_events_id_seq TO rag_runtime;

-- New RAG objects must not silently inherit application-role privileges.
ALTER DEFAULT PRIVILEGES FOR ROLE rag_owner IN SCHEMA rag
    REVOKE ALL ON TABLES FROM PUBLIC, rag_ingest, rag_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE rag_owner IN SCHEMA rag
    REVOKE ALL ON SEQUENCES FROM PUBLIC, rag_ingest, rag_runtime;

-- Deployment attestation marker. PostgreSQL health must remain unhealthy until
-- this row exists, so an existing volume cannot silently start n8n with the
-- pre-hardening privilege state.
CREATE TABLE IF NOT EXISTS rag.security_migrations (
    migration_id     TEXT PRIMARY KEY,
    applied_revision TEXT NOT NULL,
    applied_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    applied_by       TEXT NOT NULL DEFAULT current_user
);
ALTER TABLE rag.security_migrations OWNER TO rag_owner;
REVOKE ALL ON rag.security_migrations FROM PUBLIC, rag_ingest, rag_runtime;
INSERT INTO rag.security_migrations (migration_id, applied_revision, applied_by)
VALUES ('rag-security-hardening-v1', '4', current_user)
ON CONFLICT (migration_id) DO UPDATE
SET applied_revision = EXCLUDED.applied_revision,
    applied_at = now(),
    applied_by = EXCLUDED.applied_by;

CREATE OR REPLACE FUNCTION rag.create_corpus_candidate(
    p_corpus_version TEXT,
    p_document_count INTEGER,
    p_chunk_count INTEGER,
    p_embedding_profile_id TEXT
)
RETURNS TABLE (
    corpus_version TEXT,
    status TEXT,
    document_count INTEGER,
    chunk_count INTEGER,
    embedding_profile_id TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, pg_catalog
AS $function$
BEGIN
    IF NULLIF(trim(p_corpus_version), '') IS NULL
       OR NULLIF(trim(p_embedding_profile_id), '') IS NULL
       OR p_document_count IS NULL OR p_document_count <= 0
       OR p_chunk_count IS NULL OR p_chunk_count <= 0 THEN
        RAISE EXCEPTION 'candidate metadata rejected';
    END IF;

    INSERT INTO rag.corpus_versions (
        corpus_version, status, document_count, chunk_count, embedding_profile_id
    )
    VALUES (p_corpus_version, 'staging', p_document_count, p_chunk_count, p_embedding_profile_id)
    ON CONFLICT ON CONSTRAINT corpus_versions_pkey DO UPDATE
    SET document_count = CASE
            WHEN rag.corpus_versions.status = 'failed' THEN EXCLUDED.document_count
            ELSE rag.corpus_versions.document_count
        END,
        chunk_count = CASE
            WHEN rag.corpus_versions.status = 'failed' THEN EXCLUDED.chunk_count
            ELSE rag.corpus_versions.chunk_count
        END,
        embedding_profile_id = CASE
            WHEN rag.corpus_versions.status = 'failed' THEN EXCLUDED.embedding_profile_id
            ELSE rag.corpus_versions.embedding_profile_id
        END,
        status = CASE
            WHEN rag.corpus_versions.status = 'failed' THEN 'staging'
            ELSE rag.corpus_versions.status
        END,
        failed_at = CASE
            WHEN rag.corpus_versions.status = 'failed' THEN NULL
            ELSE rag.corpus_versions.failed_at
        END,
        failure_reason = CASE
            WHEN rag.corpus_versions.status = 'failed' THEN NULL
            ELSE rag.corpus_versions.failure_reason
        END
    WHERE rag.corpus_versions.embedding_profile_id = EXCLUDED.embedding_profile_id;

    RETURN QUERY
    SELECT cv.corpus_version, cv.status, cv.document_count, cv.chunk_count,
           cv.embedding_profile_id
    FROM rag.corpus_versions cv
    WHERE cv.corpus_version = p_corpus_version;
END
$function$;

CREATE OR REPLACE FUNCTION rag.stage_chunks(
    p_corpus_version TEXT,
    p_chunks JSONB,
    p_embedding_profile_id TEXT
)
RETURNS TABLE (
    corpus_version TEXT,
    embedding_profile_id TEXT,
    inserted_chunk_count INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, pg_catalog
AS $function$
DECLARE
    candidate_status TEXT;
    candidate_profile TEXT;
    inserted_count INTEGER;
BEGIN
    IF jsonb_typeof(p_chunks) <> 'array'
       OR NULLIF(trim(p_corpus_version), '') IS NULL
       OR NULLIF(trim(p_embedding_profile_id), '') IS NULL THEN
        RAISE EXCEPTION 'chunk batch rejected';
    END IF;

    SELECT cv.status, cv.embedding_profile_id
    INTO candidate_status, candidate_profile
    FROM rag.corpus_versions cv
    WHERE cv.corpus_version = p_corpus_version
    FOR UPDATE;

    IF candidate_status IS NULL OR candidate_profile <> p_embedding_profile_id THEN
        RAISE EXCEPTION 'candidate profile rejected';
    END IF;

    -- An active corpus is immutable to the ingest identity. An identical
    -- rerun is accepted only when every supplied chunk already matches; no
    -- new or changed row can be added to an active corpus.
    IF candidate_status = 'active' THEN
        IF EXISTS (
            SELECT 1
            FROM jsonb_to_recordset(p_chunks) AS c(
                source_name TEXT,
                source_hash TEXT,
                chunk_index INTEGER,
                content TEXT,
                embedding JSONB,
                embedding_profile_id TEXT
            )
            LEFT JOIN rag.documents d
              ON d.corpus_version = p_corpus_version
             AND d.source_name = c.source_name
             AND d.source_hash = c.source_hash
             AND d.chunk_index = c.chunk_index
            WHERE d.id IS NULL
               OR d.content <> c.content
               OR d.embedding_profile_id <> c.embedding_profile_id
        ) THEN
            RAISE EXCEPTION 'active candidate is immutable';
        END IF;

        RETURN QUERY SELECT p_corpus_version, p_embedding_profile_id, 0;
        RETURN;
    END IF;

    IF candidate_status <> 'staging' THEN
        RAISE EXCEPTION 'candidate is not staging';
    END IF;

    WITH inserted AS (
        INSERT INTO rag.documents (
            corpus_version, source_name, source_hash, chunk_index, content,
            embedding, embedding_profile_id, metadata
        )
        SELECT p_corpus_version,
               c.source_name,
               c.source_hash,
               c.chunk_index,
               c.content,
               c.embedding::text::vector,
               c.embedding_profile_id,
               jsonb_build_object(
                   'source_name', c.source_name,
                   'source_hash', c.source_hash,
                   'chunk_index', c.chunk_index,
                   'corpus_version', p_corpus_version,
                   'embedding_profile_id', c.embedding_profile_id
               )
        FROM jsonb_to_recordset(p_chunks) AS c(
            source_name TEXT,
            source_hash TEXT,
            chunk_index INTEGER,
            content TEXT,
            embedding JSONB,
            embedding_profile_id TEXT
        )
        WHERE c.embedding_profile_id = p_embedding_profile_id
        ON CONFLICT (corpus_version, source_hash, chunk_index) DO NOTHING
        RETURNING id
    )
    SELECT count(*)::INTEGER INTO inserted_count FROM inserted;

    RETURN QUERY SELECT p_corpus_version, p_embedding_profile_id, inserted_count;
END
$function$;

CREATE OR REPLACE FUNCTION rag.get_candidate_evidence(
    p_corpus_version TEXT,
    p_embedding_profile_id TEXT
)
RETURNS TABLE (
    corpus_version TEXT,
    status TEXT,
    document_count INTEGER,
    chunk_count INTEGER,
    embedding_profile_id TEXT,
    persisted_chunk_count INTEGER,
    persisted_document_count INTEGER
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = rag, pg_catalog
AS $function$
    SELECT cv.corpus_version,
           cv.status,
           cv.document_count,
           cv.chunk_count,
           cv.embedding_profile_id,
           count(d.id)::INTEGER AS persisted_chunk_count,
           count(DISTINCT d.source_name)::INTEGER AS persisted_document_count
    FROM rag.corpus_versions cv
    LEFT JOIN rag.documents d ON d.corpus_version = cv.corpus_version
    WHERE cv.corpus_version = p_corpus_version
      AND cv.embedding_profile_id = p_embedding_profile_id
    GROUP BY cv.corpus_version, cv.status, cv.document_count, cv.chunk_count,
             cv.embedding_profile_id;
$function$;

CREATE OR REPLACE FUNCTION rag.mark_candidate_failed(
    p_corpus_version TEXT,
    p_failure_reason TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, pg_catalog
AS $function$
BEGIN
    UPDATE rag.corpus_versions
    SET status = 'failed',
        failed_at = now(),
        failure_reason = left(COALESCE(p_failure_reason, 'unknown_failure'), 240)
    WHERE corpus_version = p_corpus_version
      AND status = 'staging';
END
$function$;

CREATE OR REPLACE FUNCTION rag.activate_corpus(
    p_corpus_version TEXT,
    p_embedding_profile_id TEXT
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = rag, pg_catalog
AS $function$
DECLARE
    activated_count INTEGER;
BEGIN
    UPDATE rag.corpus_versions
    SET status = 'superseded'
    WHERE status = 'active'
      AND corpus_version <> p_corpus_version
      AND EXISTS (
          SELECT 1
          FROM rag.corpus_versions candidate
          WHERE candidate.corpus_version = p_corpus_version
            AND candidate.status IN ('staging', 'active')
            AND candidate.embedding_profile_id = p_embedding_profile_id
            AND candidate.chunk_count = (
                SELECT count(*) FROM rag.documents d
                WHERE d.corpus_version = candidate.corpus_version
            )
            AND candidate.document_count = (
                SELECT count(DISTINCT d.source_name) FROM rag.documents d
                WHERE d.corpus_version = candidate.corpus_version
            )
      );

    UPDATE rag.corpus_versions candidate
    SET status = 'active',
        activated_at = COALESCE(candidate.activated_at, now()),
        failed_at = NULL,
        failure_reason = NULL
    WHERE candidate.corpus_version = p_corpus_version
      AND candidate.status IN ('staging', 'active')
      AND candidate.embedding_profile_id = p_embedding_profile_id
      AND candidate.chunk_count = (
          SELECT count(*) FROM rag.documents d
          WHERE d.corpus_version = candidate.corpus_version
      )
      AND candidate.document_count = (
          SELECT count(DISTINCT d.source_name) FROM rag.documents d
          WHERE d.corpus_version = candidate.corpus_version
      );

    GET DIAGNOSTICS activated_count = ROW_COUNT;
    IF activated_count <> 1 THEN
        RAISE EXCEPTION 'candidate activation rejected for corpus/profile';
    END IF;

    UPDATE rag.rag_settings
    SET active_corpus_version = p_corpus_version,
        updated_at = now()
    WHERE id = 1
      AND embedding_profile_id = p_embedding_profile_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'settings activation rejected for embedding profile';
    END IF;
END
$function$;

ALTER FUNCTION rag.activate_corpus(TEXT, TEXT) OWNER TO rag_owner;
REVOKE ALL ON FUNCTION rag.activate_corpus(TEXT, TEXT) FROM PUBLIC, rag_runtime;
GRANT EXECUTE ON FUNCTION rag.activate_corpus(TEXT, TEXT) TO rag_ingest;

ALTER FUNCTION rag.create_corpus_candidate(TEXT, INTEGER, INTEGER, TEXT) OWNER TO rag_owner;
ALTER FUNCTION rag.stage_chunks(TEXT, JSONB, TEXT) OWNER TO rag_owner;
ALTER FUNCTION rag.get_candidate_evidence(TEXT, TEXT) OWNER TO rag_owner;
ALTER FUNCTION rag.mark_candidate_failed(TEXT, TEXT) OWNER TO rag_owner;
REVOKE ALL ON FUNCTION rag.create_corpus_candidate(TEXT, INTEGER, INTEGER, TEXT) FROM PUBLIC, rag_runtime;
REVOKE ALL ON FUNCTION rag.stage_chunks(TEXT, JSONB, TEXT) FROM PUBLIC, rag_runtime;
REVOKE ALL ON FUNCTION rag.get_candidate_evidence(TEXT, TEXT) FROM PUBLIC, rag_runtime;
REVOKE ALL ON FUNCTION rag.mark_candidate_failed(TEXT, TEXT) FROM PUBLIC, rag_runtime;
GRANT EXECUTE ON FUNCTION rag.create_corpus_candidate(TEXT, INTEGER, INTEGER, TEXT) TO rag_ingest;
GRANT EXECUTE ON FUNCTION rag.stage_chunks(TEXT, JSONB, TEXT) TO rag_ingest;
GRANT EXECUTE ON FUNCTION rag.get_candidate_evidence(TEXT, TEXT) TO rag_ingest;
GRANT EXECUTE ON FUNCTION rag.mark_candidate_failed(TEXT, TEXT) TO rag_ingest;

COMMIT;
