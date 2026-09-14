-- =============================================================================
-- Asisten Pengetahuan Internal Toko Makmur Jaya — pgvector Extension Setup
-- Architecture version: 1.2 | Environment Schema version: 1.1
-- =============================================================================
-- This script MUST be run as a superuser (bootstrap role: cluster_admin)
-- BEFORE the main schema initialization (01-schema-roles-grants.sql).
-- It installs the pgvector extension and verifies the version.
-- =============================================================================

-- Install pgvector extension (requires superuser)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Note: The VECTOR column dimension in rag.documents.embedding is set at table creation time.
-- Since RAG_EMBEDDING_DIMENSION is UNKNOWN until profiling, the documents table
-- is created without a fixed dimension in 01-schema-roles-grants.sql.
-- 
-- After RAG_EMBEDDING_DIMENSION is determined (Engineer calibration), the column
-- should be altered or the table recreated with the correct dimension.
-- 
-- Option A (recreate table - simpler for demo):
--   DROP TABLE IF EXISTS rag.documents;
--   CREATE TABLE rag.documents (..., embedding VECTOR(768), ...);
-- 
-- Option B (alter column - preserves data, but requires pgvector 0.5.0+):
--   ALTER TABLE rag.documents ALTER COLUMN embedding TYPE VECTOR(768)
--       USING embedding::vector(768);
-- 
-- Option C (create new table with correct dimension, migrate data):
--   CREATE TABLE rag.documents_v2 (..., embedding VECTOR(768), ...);
--   INSERT INTO rag.documents_v2 SELECT ..., embedding::vector(768) FROM rag.documents;
--   DROP TABLE rag.documents;
--   ALTER TABLE rag.documents_v2 RENAME TO documents;
--
-- For this demo (temporary portfolio), Option A is acceptable during calibration phase.
-- Production systems would use Option B or C.

-- HNSW index creation (run AFTER dimension is fixed and data is loaded)
-- Example for dimension 768:
-- CREATE INDEX idx_documents_embedding_hnsw
--     ON rag.documents USING hnsw (embedding vector_cos_ops)
--     WITH (m = 16, ef_construction = 64);