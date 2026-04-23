#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
# Replace with your command to run all tests
run_all_tests() {
    # Make the cargo toolchain installed by the Dockerfile reachable.
    export PATH="/usr/local/cargo/bin:${HOME}/.cargo/bin:${PATH}"

    # The pytest suite resolves the user's blink_tree crate from this
    # path (mounted at /app by the evaluator). Override only if needed.
    export BLINK_TREE_CRATE="${BLINK_TREE_CRATE:-/app}"

    # The injected codebase may carry a pre-built ./target whose ELF
    # binaries lost their executable bit during the unzip step. Drop it
    # so cargo rebuilds cleanly in the container (where new artifacts
    # land with +x set correctly).
    rm -rf "${BLINK_TREE_CRATE}/target" 2>/dev/null || true

    # Locate the tests directory next to this script first (when run
    # from /eval_assets), then fall back to the canonical location.
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -d "${SCRIPT_DIR}/tests" ]; then
        TESTS_DIR="${SCRIPT_DIR}/tests"
    elif [ -d "/eval_assets/tests" ]; then
        TESTS_DIR="/eval_assets/tests"
    else
        TESTS_DIR="tests"
    fi

    python3 -m pytest -v --tb=short -p no:cacheprovider "${TESTS_DIR}"
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
