# PostgreSQL Initialization Scripts

## Execution Order (Critical)

These scripts must be run in the following order during initial deployment:

### 1. `01-init.sh` — **Run as superuser by the PostgreSQL image**
- Installs pgvector and creates schemas, roles, grants, and RAG tables.
- Reads role passwords only from container environment variables.
- Creates the workflow alignment columns `embedding_profile_id`, online `ai_timeout_max`, offline batch `ingest_timeout_max`, and `telegram_allowed_chat_id`.

### 2. `02-rag-schema-alignment.sql` — **Existing-volume migration**
- Adds the alignment columns idempotently when an older local volume already exists.
- The Compose init directory runs this only for a fresh database; apply it explicitly to an existing disposable local volume before importing the workflows.

## Post-Initialization (After RAG_EMBEDDING_DIMENSION is known)

After Engineer calibrates the embedding model and determines `RAG_EMBEDDING_DIMENSION`:

1. Update the `documents` table embedding column dimension (Option A - recreate):
   ```sql
   DROP TABLE IF EXISTS rag.documents;
   CREATE TABLE rag.documents (
       id BIGSERIAL PRIMARY KEY,
       corpus_version TEXT NOT NULL REFERENCES rag.corpus_versions(corpus_version) ON DELETE CASCADE,
       source_name TEXT NOT NULL,
       source_hash TEXT NOT NULL,
       chunk_index INTEGER NOT NULL,
       content TEXT NOT NULL,
       embedding VECTOR(768),  -- <-- SET ACTUAL DIMENSION HERE
       embedding_profile_id TEXT NOT NULL,
       metadata JSONB NOT NULL DEFAULT '{}',
       created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
       CONSTRAINT uq_doc_chunk UNIQUE (corpus_version, source_hash, chunk_index)
   );
   CREATE INDEX idx_documents_corpus_version ON rag.documents (corpus_version);
   CREATE INDEX idx_documents_profile ON rag.documents (corpus_version, embedding_profile_id);
   GRANT SELECT ON rag.documents TO rag_runtime;
   GRANT ALL ON rag.documents TO rag_ingest;
   ```

2. Create HNSW vector index (after data is loaded):
   ```sql
   CREATE INDEX idx_documents_embedding_hnsw
       ON rag.documents USING hnsw (embedding vector_cos_ops)
       WITH (m = 16, ef_construction = 64);
   ```

## Role Passwords

Actual passwords are injected at container startup via environment variables:
- `RAG_INGEST_DB_PASSWORD` → `rag_ingest` role
- `RAG_RUNTIME_DB_PASSWORD` → `rag_runtime` role
- `N8N_DB_PASSWORD` → `n8n_app` role
- `POSTGRES_PASSWORD` → `cluster_admin` role

The placeholder passwords in `01-schema-roles-grants.sql` are overwritten by the PostgreSQL container's initialization mechanism when the container starts with the actual environment variables.

## Verification

After initialization, verify:
```sql
-- Check schemas
SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('n8n', 'rag');

-- Check roles
SELECT rolname FROM pg_roles WHERE rolname IN ('n8n_app', 'rag_ingest', 'rag_runtime');

-- Check tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'rag';

-- Check pgvector
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Check initial rag_settings
SELECT * FROM rag.rag_settings;
```

## Environment Profiles

| Profile | Database Host | Database Name | Notes |
|---------|---------------|---------------|-------|
| `local-isolated` | `postgres` (Compose service) | `automation` | Unique project name, test volumes |
| `demo-vps` | `postgres` (Compose service) | `automation` | Fixed project name, persistent volumes |
