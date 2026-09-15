#!/usr/bin/env bash
# =============================================================================
# Asisten Pengetahuan Internal Toko Makmur Jaya — local-isolated launcher
# Profile: local-isolated | Created: 2026-09-14
# Usage: bash deploy/start-local.sh
# Working directory: project root (script auto-detects)
# =============================================================================

set -euo pipefail

# Resolve project root (parent of deploy/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

COMPOSE_FILE="deploy/compose.yaml"
PROJECT_NAME="rag-local"
ENV_FILE=".env.test"

echo "=== Asisten Pengetahuan Internal Toko Makmur Jaya ==="
echo "Profile: local-isolated"
echo "Compose: $COMPOSE_FILE"
echo "Project: $PROJECT_NAME"
echo "Env:     $ENV_FILE"
echo ""

# Preflight: check required files exist
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "ERROR: Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi
if [ ! -f "$ENV_FILE" ]; then
  echo "ERROR: Env file not found: $ENV_FILE" >&2
  echo "Copy .env.test and fill in secrets before starting." >&2
  exit 1
fi
if [ ! -d "docs" ]; then
  echo "ERROR: docs/ directory not found" >&2
  exit 1
fi

# Preflight: validate compose config (quiet mode per acceptance contract)
echo "Running compose config validation..."
docker compose -f "$COMPOSE_FILE" --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" config --quiet
echo "Compose config: OK"

# Start services
echo ""
echo "Starting services..."
docker compose -f "$COMPOSE_FILE" --project-name "$PROJECT_NAME" --env-file "$ENV_FILE" up -d

echo ""
echo "Waiting for health checks..."
echo "  n8n:       http://127.0.0.1:5678 (loopback only)"
echo "  PostgreSQL: internal (no host port)"
echo ""

# Show status
docker compose -f "$COMPOSE_FILE" --project-name "$PROJECT_NAME" ps

echo ""
echo "=== Stack started ==="
echo "n8n UI: http://127.0.0.1:5678"
echo "Stop:  bash deploy/stop-local.sh"
