#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
    echo "Running all tests..."
    REAL_SCRIPT="$(readlink -f "${BASH_SOURCE[0]}")"
    SCRIPT_DIR="$(cd "$(dirname "$REAL_SCRIPT")" && pwd)"
    if [ -f "${SCRIPT_DIR}/run_tests.py" ]; then
        TEST_FILE="${SCRIPT_DIR}/run_tests.py"
    elif [ -f "${SCRIPT_DIR}/tests/run_tests.py" ]; then
        TEST_FILE="${SCRIPT_DIR}/tests/run_tests.py"
    else
        echo "ERROR: run_tests.py not found in ${SCRIPT_DIR} or ${SCRIPT_DIR}/tests" >&2
        exit 1
    fi
    PYTHONPATH=/app python3 -m pytest "$TEST_FILE" \
        -v --tb=short -p no:cacheprovider 2>&1 || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests