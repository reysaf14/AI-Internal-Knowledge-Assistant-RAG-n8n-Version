#!/usr/bin/env bash
# =============================================================================
# Asisten Pengetahuan Internal Toko Makmur Jaya — local-isolated stop
# Profile: local-isolated | Created: 2026-09-14
# Usage: bash deploy/stop-local.sh
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

COMPOSE_FILE="deploy/compose.yaml"
PROJECT_NAME="rag-local"
ENV_FILE=".env.test"

echo "Stopping local-isolated stack..."
docker compose -f "$COMPOSE_FILE" --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" down

echo ""
echo "=== Stack stopped ==="
echo "Volumes preserved. To remove volumes:"
echo "  docker compose -f $COMPOSE_FILE --project-name $PROJECT_NAME --env-file $ENV_FILE down -v"
