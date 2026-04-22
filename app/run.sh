#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
  echo "Running all tests..."

  SCRIPT_PATH="${BASH_SOURCE[0]}"
  if [ -L "$SCRIPT_PATH" ]; then
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH" 2>/dev/null || readlink "$SCRIPT_PATH")"
  fi
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
  cd "$SCRIPT_DIR"

  if [ -d /eval_assets/tests ] && [ -f /eval_assets/run_tests ]; then
    # Docker eval: tests in /eval_assets; codebase (app/*) extracted at /app
    export REAL_CODER_ROOT=/app
    TESTS_PATH="/eval_assets/tests"
  else
    TESTS_PATH="$SCRIPT_DIR/tests"
    if [ -z "${REAL_CODER_ROOT:-}" ] && [ -d "$SCRIPT_DIR/app" ]; then
      export REAL_CODER_ROOT="$SCRIPT_DIR"
    elif [ -z "${REAL_CODER_ROOT:-}" ] && [ -d "$SCRIPT_DIR/codebase/app" ]; then
      export REAL_CODER_ROOT="$SCRIPT_DIR/codebase"
    else
      export REAL_CODER_ROOT="${REAL_CODER_ROOT:-$SCRIPT_DIR}"
    fi
  fi

  if command -v python3.11 &>/dev/null; then
    PYTHON=python3.11
  elif command -v python3 &>/dev/null; then
    PYTHON=python3
  else
    PYTHON=python
  fi

  (
    cd "${REAL_CODER_ROOT:-/app}"
    PYTHONUNBUFFERED=1 PYTHONPATH="${REAL_CODER_ROOT:-/app}:$PYTHONPATH" "$PYTHON" -m pytest "$TESTS_PATH" -v --tb=short --no-header --rootdir="$SCRIPT_DIR"
  )
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
