#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        # Validation environment: tests live in /eval_assets, codebase lives in /app.
        # PYTHONPATH=/app lets the test suite resolve pipeline.* imports from the codebase.
        cd /eval_assets
        PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
    elif [ -d /app/tests ]; then
        # Docker container with the full codebase already at /app.
        cd /app
        python -m pytest tests/ -v --tb=short --no-header
    else
        # Local development: resolve the repo root from this script's location.
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$SCRIPT_DIR"
        python -m pytest tests/ -v --tb=short --no-header
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
