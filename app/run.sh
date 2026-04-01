#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
 
    # Make Go available on PATH for this script's execution context.
    # The binary lives at /usr/local/go/bin (installed in Dockerfile).
    # ENV instructions in the Dockerfile do not persist into exec'd shells
    # invoked by validation.sh, so we set the environment explicitly here.
    export PATH="/usr/local/go/bin:${PATH}"
    export GOPATH="/root/go"
    export GOMODCACHE="/root/go/pkg/mod"
 
    # Resolve the directory that contains this script, following symlinks.
    # readlink -f resolves the full real path; BASH_SOURCE[0] is the script
    # itself even when invoked via a symlink (as validation.sh does).
    SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

    # ------------------------------------------------------------------
    # Locate the test directory.
    # Priority:
    #   1. /eval_assets/tests  -- validation.sh context
    #   2. $SCRIPT_DIR/tests   -- run from codebase root directly
    # ------------------------------------------------------------------
    if [ -d "/eval_assets/tests" ]; then
        TEST_DIR="/eval_assets/tests"
        BINARY_DIR="/eval_assets"
    elif [ -d "$SCRIPT_DIR/tests" ]; then
        TEST_DIR="$SCRIPT_DIR/tests"
        BINARY_DIR="$SCRIPT_DIR"
    else
        echo "ERROR: test directory not found" >&2
        exit 1
    fi

    # ------------------------------------------------------------------
    # Attempt to build the md2slides binary.
    #
    # On an EMPTY CODEBASE (F2P baseline run) main.go will not exist yet.
    # In that case we skip the build entirely and proceed straight to
    # pytest. The test helper _run() calls pytest.fail() when the binary
    # is absent, so every test records FAILED (not ERROR) -- which is
    # exactly the required before.json state for Fail-to-Pass validation.
    #
    # || true on go build ensures a compilation error in a partial
    # codebase also does not abort this script before pytest runs.
    # ------------------------------------------------------------------
    if [ -f "/app/main.go" ]; then
        echo "Building md2slides from /app ..."
        cd /app
        go build -o "$BINARY_DIR/md2slides" . || true
    elif [ -f "$SCRIPT_DIR/main.go" ]; then
        echo "Building md2slides from $SCRIPT_DIR ..."
        cd "$SCRIPT_DIR"
        go build -o "$BINARY_DIR/md2slides" . || true
    else
        echo "No Go source found; skipping build (empty codebase run)."
    fi

    # ------------------------------------------------------------------
    # Run the pytest test suite.
    # -v           verbose output (one line per test, with PASSED/FAILED)
    # --tb=short   short traceback on failures (keeps output parseable)
    # --no-header  omit the pytest header block
    # 2>&1         merge stderr into stdout so parsing.py sees everything
    # || true      pytest exits non-zero when tests fail; do not let that
    #              abort run.sh before the output has been written
    # ------------------------------------------------------------------
    echo "Running pytest from $TEST_DIR ..."
    TEST_FILES=$(find "$TEST_DIR" -maxdepth 1 -name "test_*.py" -o -name "tests.py" | sort)
    if [ -z "$TEST_FILES" ]; then
        echo "ERROR: no test files found in $TEST_DIR" >&2
        exit 1
    fi
    python3 -m pytest $TEST_FILES -v --tb=short --no-header 2>&1 || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests