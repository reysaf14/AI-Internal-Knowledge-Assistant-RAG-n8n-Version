#!/bin/bash
# =============================================================================
# Test Launcher — Local-Isolated Profile
# Asisten Pengetahuan Internal Toko Makmur Jaya
# Architecture version: 1.2 | Environment Schema version: 1.1
# =============================================================================
# Purpose: Launch Docker Compose stack for local-isolated testing with
# synthetic fixtures, provider mock, and fail-closed behavior.
#
# Usage:
#   bash scripts/test-local.sh [up|down|reset|logs]
#
# Environment:
#   - Uses .env.test (must exist; see .env.example)
#   - Unique project name: rag-test-$(date +%s)
#   - Compose file: deploy/compose.yaml (to be created by DevOps)
#   - Profile: local (when Compose supports it)
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_TEST_FILE="$PROJECT_ROOT/.env.test"
COMPOSE_FILE="$PROJECT_ROOT/deploy/compose.yaml"
PROJECT_NAME="rag-test-$(date +%s)"
COMPOSE_PROJECT_NAME="$PROJECT_NAME"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose not found. Please install Docker Compose."
        exit 1
    fi
    
    # Check .env.test
    if [ ! -f "$ENV_TEST_FILE" ]; then
        log_error ".env.test not found at $ENV_TEST_FILE"
        log_info "Copy from .env.example: cp $PROJECT_ROOT/.env.example $ENV_TEST_FILE"
        log_info "Then fill in required values."
        exit 1
    fi
    
    # Check compose.yaml
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "deploy/compose.yaml not found. This should be created by DevOps."
        log_info "Expected path: $COMPOSE_FILE"
        exit 1
    fi
    
    log_info "All prerequisites met."
}

validate_env_file() {
    log_info "Validating .env.test..."
    
    # Source the env file (in subshell to avoid polluting environment)
    (
        set -a
        source "$ENV_TEST_FILE"
        set +a
        
        # Check required variables (non-secret)
        local required_vars=(
            "N8N_IMAGE"
            "PGVECTOR_IMAGE"
            "GENERIC_TIMEZONE"
            "POSTGRES_DB"
        )
        
        for var in "${required_vars[@]}"; do
            value="${!var:-}"
            if [ -z "$value" ] || [ "$value" = "" ]; then
                log_error "Required variable $var is empty in .env.test"
                exit 1
            fi
        done
        
        log_info "All required env vars are set (non-empty)."
    ) || exit 1
}

up() {
    log_info "Starting Docker Compose stack (project: $PROJECT_NAME)..."
    
    docker-compose \
        --file "$COMPOSE_FILE" \
        --project-name "$PROJECT_NAME" \
        --env-file "$ENV_TEST_FILE" \
        up -d
    
    log_info "Stack started. Project name: $PROJECT_NAME"
    log_info "To view logs: docker-compose -p $PROJECT_NAME logs -f"
}

down() {
    log_info "Stopping Docker Compose stack (project: $PROJECT_NAME)..."
    
    docker-compose \
        --file "$COMPOSE_FILE" \
        --project-name "$PROJECT_NAME" \
        down
    
    log_info "Stack stopped."
}

reset() {
    log_warn "Resetting stack (removing volumes)..."
    log_warn "This will delete all data. Continue? (yes/no)"
    read -r response
    
    if [ "$response" != "yes" ]; then
        log_info "Reset cancelled."
        return
    fi
    
    docker-compose \
        --file "$COMPOSE_FILE" \
        --project-name "$PROJECT_NAME" \
        down -v
    
    log_info "Stack reset complete."
}

logs() {
    log_info "Showing logs (project: $PROJECT_NAME)..."
    docker-compose \
        --file "$COMPOSE_FILE" \
        --project-name "$PROJECT_NAME" \
        logs -f
}

# =============================================================================
# Main
# =============================================================================

main() {
    local action="${1:-up}"
    
    log_info "Local-Isolated Test Launcher"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Compose file: $COMPOSE_FILE"
    log_info "Env file: $ENV_TEST_FILE"
    log_info "Project name: $PROJECT_NAME"
    echo ""
    
    check_prerequisites
    validate_env_file
    echo ""
    
    case "$action" in
        up)
            up
            ;;
        down)
            down
            ;;
        reset)
            reset
            ;;
        logs)
            logs
            ;;
        *)
            log_error "Unknown action: $action"
            echo "Usage: $0 [up|down|reset|logs]"
            exit 1
            ;;
    esac
}

main "$@"