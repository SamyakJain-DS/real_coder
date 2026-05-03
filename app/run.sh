#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        # Sandbox: tests in /eval_assets, codebase in /app
        cd /eval_assets
        PYTHONPATH=/app:"${PYTHONPATH:-}" python -m pytest tests/ -v --tb=short --no-header -W ignore 2>&1
    elif [ -d /app/tests ]; then
        # Local Docker with codebase mounted at /app
        cd /app
        python -m pytest tests/ -v --tb=short --no-header -W ignore 2>&1
    else
        # Fallback: run from the directory containing this script
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$SCRIPT_DIR"
        PYTHON=$(command -v python 2>/dev/null || command -v python3)
        $PYTHON -m pytest tests/ -v --tb=short --no-header -W ignore 2>&1
    fi
}
# --- END CONFIGURATION SECTION ---
run_all_tests
