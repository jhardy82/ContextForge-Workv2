#!/bin/bash
# =============================================================================
# Agent CLI Entrypoint - Structured Output for AI Coding Agents
# =============================================================================
# OUTPUT FORMAT: JSON-Lines (JSONL) to stderr for status, stdout for commands
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Structured logging function - outputs JSONL to stderr
# -----------------------------------------------------------------------------
log_event() {
    local event_type="$1"
    local message="$2"
    local status="${3:-info}"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

    # Output to stderr so command output remains clean on stdout
    echo "{\"timestamp\":\"${timestamp}\",\"event\":\"${event_type}\",\"message\":\"${message}\",\"status\":\"${status}\",\"container\":\"agent-cli\"}" >&2
}

# -----------------------------------------------------------------------------
# Emit container initialization event
# -----------------------------------------------------------------------------
emit_init() {
    log_event "container_init" "Agent CLI container starting" "info"
    log_event "environment" "CF_OUTPUT_FORMAT=${CF_OUTPUT_FORMAT:-text}" "info"
    log_event "environment" "CF_AGENT_MODE=${CF_AGENT_MODE:-0}" "info"
    log_event "environment" "DATABASE_URL=${DATABASE_URL:+[REDACTED]}" "info"
}

# -----------------------------------------------------------------------------
# Database connectivity check - JSON output
# -----------------------------------------------------------------------------
check_database() {
    if [ -n "$DATABASE_URL" ]; then
        log_event "db_check" "Testing database connectivity" "info"

        if pg_isready -d "$DATABASE_URL" >/dev/null 2>&1; then
            log_event "db_check" "Database connection successful" "success"
            return 0
        else
            log_event "db_check" "Database connection failed" "error"
            return 1
        fi
    else
        log_event "db_check" "DATABASE_URL not set - skipping" "warning"
        return 0
    fi
}

# -----------------------------------------------------------------------------
# Emit ready event with capability manifest
# -----------------------------------------------------------------------------
emit_ready() {
    local capabilities='["psql","python","cf_core","alembic","jq"]'
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")

    echo "{\"timestamp\":\"${timestamp}\",\"event\":\"container_ready\",\"status\":\"ready\",\"container\":\"agent-cli\",\"capabilities\":${capabilities}}" >&2
}

# -----------------------------------------------------------------------------
# Trap for structured exit events
# -----------------------------------------------------------------------------
trap_exit() {
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        log_event "container_exit" "Agent CLI container exiting normally" "success"
    else
        log_event "container_exit" "Agent CLI container exiting with code ${exit_code}" "error"
    fi
}
trap trap_exit EXIT

# -----------------------------------------------------------------------------
# Main entrypoint logic
# -----------------------------------------------------------------------------
main() {
    emit_init

    # Check database if URL provided
    check_database || true  # Don't fail on DB issues

    emit_ready

    # Execute command passed to container
    if [ $# -gt 0 ]; then
        log_event "command_exec" "Executing: $*" "info"
        exec "$@"
    else
        # Interactive mode
        log_event "interactive" "Starting interactive shell" "info"
        exec /bin/bash
    fi
}

main "$@"
