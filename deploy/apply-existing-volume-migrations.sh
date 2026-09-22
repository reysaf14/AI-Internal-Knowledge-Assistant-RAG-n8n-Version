#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${1:-.env.test}"
ENV_PATH="$PROJECT_ROOT/$ENV_FILE"

test -f "$ENV_PATH" || { echo "Environment file not found: $ENV_PATH" >&2; exit 2; }

docker compose -f "$PROJECT_ROOT/deploy/compose.yaml" \
  --project-name rag-local --env-file "$ENV_PATH" up -d postgres

for migration in 02-rag-schema-alignment.sql 03-rag-security-hardening.sql; do
  echo "[rag-migrate] applying $migration"
  docker exec -i rag-postgres-local sh -c \
    'psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"' \
    < "$PROJECT_ROOT/deploy/postgres-init/$migration"
done

marker="$(docker exec rag-postgres-local sh -c \
  'psql -X -qAt --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "SELECT migration_id || ''|'' || applied_revision FROM rag.security_migrations WHERE migration_id = ''rag-security-hardening-v1'' AND applied_revision = ''4''"')"
test "$marker" = 'rag-security-hardening-v1|4' || {
  echo "Security migration marker not verified: $marker" >&2
  exit 1
}
echo "[rag-migrate] verified $marker"
echo '[rag-migrate] PostgreSQL is ready; restart/start n8n after this command.'
