#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        PYTHONPATH=/app python3 -m pytest /eval_assets/tests/ -v --tb=short --no-header
    elif [ -d "$(dirname "${BASH_SOURCE[0]}")/tests" ]; then
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        PYTHONPATH=/app python3 -m pytest "${SCRIPT_DIR}/tests/" -v --tb=short --no-header
    else
        echo "ERROR: no tests/ directory found." >&2
        exit 1
    fi
}
# --- END CONFIGURATION SECTION ---
run_all_tests
