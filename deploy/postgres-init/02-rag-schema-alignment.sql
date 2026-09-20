-- =============================================================================
-- Existing-volume migration for the workflow/schema alignment.
-- Fresh volumes receive the same columns from 01-init.sh.
-- No secret or payload is stored here.
-- =============================================================================

ALTER TABLE rag.rag_settings
    ADD COLUMN IF NOT EXISTS ai_timeout_max INTEGER,
    ADD COLUMN IF NOT EXISTS ingest_timeout_max INTEGER,
    ADD COLUMN IF NOT EXISTS telegram_allowed_chat_id TEXT;

ALTER TABLE rag.documents
    ADD COLUMN IF NOT EXISTS embedding_profile_id TEXT;

CREATE INDEX IF NOT EXISTS idx_documents_profile
    ON rag.documents (corpus_version, embedding_profile_id);

GRANT SELECT ON rag.rag_settings, rag.documents TO rag_runtime;
GRANT ALL PRIVILEGES ON rag.rag_settings, rag.documents TO rag_ingest;
