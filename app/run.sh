#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  if [ -n "${BASH_SOURCE[0]:-}" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}" 2>/dev/null || echo "${BASH_SOURCE[0]}")")" && pwd)"
  else
    SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")" && pwd)"
  fi

  TEST_DIR="$SCRIPT_DIR"
  if [ -d "$SCRIPT_DIR/tests" ]; then
    TEST_DIR="$SCRIPT_DIR/tests"
  fi

  export PYTHONPATH="/app:${PYTHONPATH:-}"

  cd "$TEST_DIR"
  # Emit pytest's verbose per-test status so parsing.py can convert each
  # "<nodeid> PASSED|FAILED|SKIPPED [pct%]" line into a structured entry.
  python3 -m pytest --no-header --tb=no -v --color=no -p no:cacheprovider || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
