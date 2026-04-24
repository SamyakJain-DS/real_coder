#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  if [ -d /eval_assets/tests ]; then
    # Running inside the validation container:
    # tests live in /eval_assets/tests, codebase lives in /app
    cd /eval_assets
    PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short -W ignore 2>&1 || true
  elif [ -d /app/tests ]; then
    # Running inside a plain Docker container with the full codebase at /app
    cd /app
    python -m pytest tests/ -v --tb=short -W ignore 2>&1 || true
  else
    # Fallback: resolve the directory that contains this script and run from there
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}" python -m pytest tests/ -v --tb=short -W ignore 2>&1 || true
  fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
