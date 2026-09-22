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
    docker compose @compose up -d postgres | Out-Host

    foreach ($migration in @('02-rag-schema-alignment.sql', '03-rag-security-hardening.sql')) {
        $path = Join-Path $projectRoot "deploy/postgres-init/$migration"
        Write-Host "[rag-migrate] applying $migration"
        Get-Content -Raw -LiteralPath $path |
            docker exec -i rag-postgres-local sh -c 'psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"' |
            Out-Host
        if ($LASTEXITCODE -ne 0) {
            throw "Migration failed: $migration"
        }
    }

    $attestation = docker exec rag-postgres-local sh -c 'psql -X -qAt --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "SELECT migration_id || ''|'' || applied_revision FROM rag.security_migrations WHERE migration_id = ''rag-security-hardening-v1'' AND applied_revision = ''4''"'
    if ($LASTEXITCODE -ne 0 -or $attestation.Trim() -ne 'rag-security-hardening-v1|4') {
        throw "Security migration marker not verified: $attestation"
    }
    Write-Host "[rag-migrate] verified $attestation"
    Write-Host '[rag-migrate] PostgreSQL is ready; restart/start n8n after this command.'
}
finally {
    Pop-Location
}
