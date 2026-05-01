#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        cd /eval_assets
        PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
    elif [ -d "$(dirname "${BASH_SOURCE[0]}")/tests" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$SCRIPT_DIR"
        PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}" python -m pytest tests/ -v --tb=short --no-header
    else
        echo "ERROR: no tests/ directory found." >&2
        exit 1
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
