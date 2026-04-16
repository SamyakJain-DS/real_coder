#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
  echo "Running all tests..."
  if [ -d /eval_assets/tests ]; then
    # Validation context: tests live in /eval_assets, codebase in /app
    cd /eval_assets
    PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
  elif [ -d /app/tests ]; then
    # Docker context with codebase mounted at /app
    cd /app
    python -m pytest tests/ -v --tb=short --no-header
  else
    # Local context: run from the directory containing this script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHON=$(command -v python 2>/dev/null || command -v python3)
    $PYTHON -m pytest tests/ -v --tb=short --no-header
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests