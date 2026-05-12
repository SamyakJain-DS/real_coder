#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
# Replace with your command to run all tests
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        cd /app
        PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest /eval_assets/tests/ -v --tb=short --no-header
    elif [ -d /app/tests ]; then
        # Running locally inside a Docker container with tests in /app/tests/
        cd /app
        PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
    else
        # Fallback: derive paths from this script's location
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$SCRIPT_DIR"
        PYTHONPATH="$SCRIPT_DIR":${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests