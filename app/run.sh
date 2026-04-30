#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")" && pwd)"
    TEST_DIR="$SCRIPT_DIR"
    [ -d "$SCRIPT_DIR/tests" ] && TEST_DIR="$SCRIPT_DIR/tests"

    export PYTHONPATH="/app:${PYTHONPATH:-}"
    cd /app
    python3 -m pytest "$TEST_DIR" --no-header --tb=no -v --color=no -p no:cacheprovider || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
