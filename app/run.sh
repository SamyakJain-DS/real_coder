#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
 
    # Find the test file. In the sandbox (validation.sh), tests live under /eval_assets.
    # When running locally with the codebase mounted at /app, tests live under /app.
    TEST_FILE=""
    for ROOT in /eval_assets/tests /eval_assets /app/tests /app; do
        if [ ! -d "$ROOT" ]; then
            continue
        fi
        CAND="$(find "$ROOT" -maxdepth 3 \( -name 'test_*.py' -o -name 'test.py' \) \
                -not -path '*/__pycache__/*' 2>/dev/null | sort | head -1)"
        if [ -n "$CAND" ]; then
            TEST_FILE="$CAND"
            break
        fi
    done
 
    if [ -z "$TEST_FILE" ]; then
        echo "ERROR: no test file found under /eval_assets or /app" >&2
        exit 1
    fi
 
    echo "Test file: $TEST_FILE"
 
    # Codebase always lives in /app (injected by validation.sh for the after-run;
    # absent for the before-run so the fixture yields a dead URL and all tests FAIL).
    APP_DIR="/app" python3 -m pytest "$TEST_FILE" -v --tb=short --no-header --color=no || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests