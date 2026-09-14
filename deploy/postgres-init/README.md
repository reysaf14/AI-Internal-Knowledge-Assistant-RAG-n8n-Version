# PostgreSQL Initialization Scripts

## Execution Order (Critical)

These scripts must be run in the following order during initial deployment:

### 1. `00-pgvector-extension.sql` — **Run as superuser (bootstrap role)**
- Installs `pgvector` extension
- Must run before any table with `VECTOR` column type
- Run with: `psql -U cluster_admin -d automation -f 00-pgvector-extension.sql`

### 2. `01-schema-roles-grants.sql` — **Run as superuser (bootstrap role)**
- Creates schemas: `n8n`, `rag`
- Creates roles: `rag_ingest`, `rag_runtime` (passwords are placeholders — actual passwords set via environment variables at container startup)
- Grants permissions
- Creates all RAG tables: `rag_settings`, `corpus_versions`, `documents`, `telegram_updates`, `safe_events`
- Inserts initial `rag_settings` row (config_revision = 'UNINITIALIZED')
- Run with: `psql -U cluster_admin -d automation -f 01-schema-roles-grants.sql`

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
       metadata JSONB NOT NULL DEFAULT '{}',
       created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
       CONSTRAINT uq_doc_chunk UNIQUE (corpus_version, source_hash, chunk_index)
   );
   CREATE INDEX idx_documents_corpus_version ON rag.documents (corpus_version);
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