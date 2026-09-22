param(
    [string]$EnvFile = '.env.test'
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $projectRoot 'deploy/compose.yaml'
$envPath = Join-Path $projectRoot $EnvFile

if (-not (Test-Path -LiteralPath $envPath)) {
    throw "Environment file not found: $envPath"
}

Push-Location $projectRoot
try {
    $compose = @('-f', $composeFile, '--project-name', 'rag-local', '--env-file', $envPath)
    Write-Host '== compose images =='
    docker compose @compose config --images

    Write-Host '== runtime image/health attestation =='
    foreach ($container in @('rag-postgres-local', 'rag-n8n-local')) {
        $image = docker inspect --format '{{.Config.Image}}' $container
        $containerId = docker inspect --format '{{.Id}}' $container
        $health = docker inspect --format '{{.State.Health.Status}}' $container
        $readOnly = docker inspect --format '{{.HostConfig.ReadonlyRootfs}}' $container
        $imageAttestation = docker image inspect --format '{{.Id}}|{{join .RepoDigests ","}}' $image
        if ($LASTEXITCODE -ne 0) {
            throw "Runtime image inspection failed: $container"
        }
        "$container|$image|$containerId|$imageAttestation|health=$health|readonly_root=$readOnly"
    }

    Write-Host '== postgres security catalog =='
    $catalogSql = @'
SELECT 'marker' AS check_name,
       EXISTS (
           SELECT 1 FROM rag.security_migrations
           WHERE migration_id = 'rag-security-hardening-v1'
             AND applied_revision = '4'
       )::text AS result;
SELECT 'ingest_create_database' AS check_name,
       has_database_privilege('rag_ingest', current_database(), 'CREATE')::text AS result;
SELECT 'ingest_create_schema' AS check_name,
       has_schema_privilege('rag_ingest', 'rag', 'CREATE')::text AS result;
SELECT 'ingest_update_settings' AS check_name,
       has_table_privilege('rag_ingest', 'rag.rag_settings', 'UPDATE')::text AS result;
SELECT 'ingest_select_documents' AS check_name,
       has_table_privilege('rag_ingest', 'rag.documents', 'SELECT')::text AS result;
SELECT 'ingest_update_corpus_versions' AS check_name,
       has_table_privilege('rag_ingest', 'rag.corpus_versions', 'UPDATE')::text AS result;
SELECT 'ingest_insert_corpus_versions' AS check_name,
       has_table_privilege('rag_ingest', 'rag.corpus_versions', 'INSERT')::text AS result;
SELECT 'ingest_insert_documents' AS check_name,
       has_table_privilege('rag_ingest', 'rag.documents', 'INSERT')::text AS result;
SELECT 'ingest_update_documents' AS check_name,
       has_table_privilege('rag_ingest', 'rag.documents', 'UPDATE')::text AS result;
SELECT 'ingest_delete_documents' AS check_name,
       has_table_privilege('rag_ingest', 'rag.documents', 'DELETE')::text AS result;
SELECT 'ingest_activate_function' AS check_name,
       has_function_privilege('rag_ingest', 'rag.activate_corpus(text,text)', 'EXECUTE')::text AS result;
SELECT 'ingest_candidate_function' AS check_name,
       has_function_privilege('rag_ingest', 'rag.create_corpus_candidate(text,integer,integer,text)', 'EXECUTE')::text AS result;
SELECT 'ingest_stage_function' AS check_name,
       has_function_privilege('rag_ingest', 'rag.stage_chunks(text,jsonb,text)', 'EXECUTE')::text AS result;
SELECT 'ingest_evidence_function' AS check_name,
       has_function_privilege('rag_ingest', 'rag.get_candidate_evidence(text,text)', 'EXECUTE')::text AS result;
SELECT 'ingest_failure_function' AS check_name,
       has_function_privilege('rag_ingest', 'rag.mark_candidate_failed(text,text)', 'EXECUTE')::text AS result;
SELECT 'runtime_update_settings' AS check_name,
       has_table_privilege('rag_runtime', 'rag.rag_settings', 'UPDATE')::text AS result;
SELECT 'rag_schema_owner' AS check_name,
       (SELECT r.rolname FROM pg_namespace n JOIN pg_roles r ON r.oid = n.nspowner WHERE n.nspname = 'rag') AS result;
SELECT 'active_corpus_count' AS check_name,
       (SELECT count(*)::text FROM rag.corpus_versions WHERE status = 'active') AS result;
SELECT 'document_count' AS check_name,
       (SELECT count(*)::text FROM rag.documents) AS result;
'@
    $catalogSql | docker exec -i rag-postgres-local sh -c 'psql -X -qAt --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"'
    if ($LASTEXITCODE -ne 0) {
        throw 'PostgreSQL security catalog verification failed'
    }

    function Assert-RoleSqlDenied {
        param(
            [Parameter(Mandatory = $true)][string]$Name,
            [Parameter(Mandatory = $true)][string]$ExpectedPattern,
            [Parameter(Mandatory = $true)][string]$Sql
        )

        $output = @($Sql | docker exec -i rag-postgres-local sh -c 'PGPASSWORD="$RAG_INGEST_DB_PASSWORD" psql -X -v ON_ERROR_STOP=1 --username rag_ingest --dbname "$POSTGRES_DB" -f -' 2>&1)
        if ($LASTEXITCODE -eq 0) {
            throw "Expected rag_ingest denial did not occur: $Name"
        }
        if (($output -join "`n") -notmatch [regex]::Escape($ExpectedPattern)) {
            throw "Unexpected rejection for $Name; expected '$ExpectedPattern' but received: $($output -join ' ')"
        }
        Write-Host "PASS: rag_ingest denied $Name"
    }

    Write-Host '== rag_ingest negative matrix =='
    Assert-RoleSqlDenied 'document content read' 'permission denied' @'
SELECT content FROM rag.documents LIMIT 1;
'@
    Assert-RoleSqlDenied 'corpus metadata update' 'permission denied' @'
UPDATE rag.corpus_versions
SET document_count = document_count
WHERE status = 'active';
'@
    Assert-RoleSqlDenied 'active corpus status update' 'permission denied' @'
UPDATE rag.corpus_versions
SET status = 'failed'
WHERE status = 'active';
'@
    Assert-RoleSqlDenied 'direct active corpus insert' 'permission denied' @'
INSERT INTO rag.corpus_versions
    (corpus_version, status, document_count, chunk_count, embedding_profile_id)
VALUES ('security-verifier-direct-active-v4', 'active', 1, 1, 'security-verifier');
'@
    Assert-RoleSqlDenied 'document delete' 'permission denied' @'
DELETE FROM rag.documents;
'@
    Assert-RoleSqlDenied 'active candidate mutation through staging function' 'active candidate is immutable' @'
SELECT rag.stage_chunks(
    (SELECT active_corpus_version FROM rag.rag_settings WHERE id = 1),
    jsonb_build_array(jsonb_build_object(
        'source_name', 'security-verifier',
        'source_hash', 'security-verifier',
        'chunk_index', 999999,
        'content', 'security-verifier',
        'embedding', '[]'::jsonb,
        'embedding_profile_id', (SELECT embedding_profile_id FROM rag.rag_settings WHERE id = 1)
    )),
    (SELECT embedding_profile_id FROM rag.rag_settings WHERE id = 1)
);
'@

    Write-Host '== rag_ingest positive function smoke =='
    $positiveSql = @'
BEGIN;
SELECT * FROM rag.get_candidate_evidence(
    (SELECT active_corpus_version FROM rag.rag_settings WHERE id = 1),
    (SELECT embedding_profile_id FROM rag.rag_settings WHERE id = 1)
);
SELECT * FROM rag.create_corpus_candidate(
    'security-verifier-staging-v4',
    1,
    1,
    (SELECT embedding_profile_id FROM rag.rag_settings WHERE id = 1)
);
ROLLBACK;
'@
    $positiveSql | docker exec -i rag-postgres-local sh -c 'PGPASSWORD="$RAG_INGEST_DB_PASSWORD" psql -X -v ON_ERROR_STOP=1 --username rag_ingest --dbname "$POSTGRES_DB" -f -' *> $null
    if ($LASTEXITCODE -ne 0) {
        throw 'rag_ingest function smoke verification failed'
    }
    Write-Host 'PASS: evidence read and staging candidate function calls succeed; transaction rolled back'

    Write-Host '== tracked evaluation runs (must be empty) =='
    $tracked = git ls-files -- evaluation/run_*
    if ($tracked) {
        $tracked
        throw 'Tracked raw evaluation runs remain in the release boundary'
    }
    Write-Host 'PASS: no evaluation/run_* files are tracked'
}
finally {
    Pop-Location
}
