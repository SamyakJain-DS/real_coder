#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        # CLI tests use cwd=<tests_dir>/.., which resolves to /eval_assets/.
        # Subprocess must find pipeline.py and data/ there.
        ln -sf /app/pipeline.py /eval_assets/pipeline.py
        ln -sf /app/data        /eval_assets/data
        cd /app
        PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest /eval_assets/tests/ -v --tb=short --no-header
    elif [ -d /app/tests ]; then
        cd /app
        PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
    else
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$SCRIPT_DIR"
        PYTHONPATH="$SCRIPT_DIR":${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests