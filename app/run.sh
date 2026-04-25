#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---

run_all_tests() {
  if [ -d /eval_assets ] && [ -n "$(find /eval_assets -maxdepth 2 -name 'test_*.py' 2>/dev/null | head -1)" ]; then
    TESTS_DIR="/eval_assets/tests"
    APP_DIR="/app"
    SCRIPT_DIR="/eval_assets"
    if [ -d "$APP_DIR/data" ] && [ ! -e "$SCRIPT_DIR/data" ]; then
      ln -sf "$APP_DIR/data" "$SCRIPT_DIR/data"
    fi
    if [ -f "$APP_DIR/pyproject.toml" ] && [ ! -e "$SCRIPT_DIR/pyproject.toml" ]; then
      ln -sf "$APP_DIR/pyproject.toml" "$SCRIPT_DIR/pyproject.toml"
    fi
  else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    APP_DIR="$SCRIPT_DIR"
    TESTS_DIR="$SCRIPT_DIR/tests"
  fi

  ROOTDIR="$(dirname "$TESTS_DIR")"

  PYTHONPATH="$APP_DIR${PYTHONPATH:+:$PYTHONPATH}" python -m pytest "$TESTS_DIR" \
    --rootdir="$ROOTDIR" -v --tb=short --no-header -p no:cacheprovider || true
}

# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
