#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
 
  if [ -d /eval_assets/tests ]; then
    # Running inside validation container: tests in /eval_assets, code in /app
    cd /app
    PYTHONPATH=/app python -m pytest /eval_assets/tests/ -v --tb=short --no-header 2>&1
  elif [ -d /app/tests ]; then
    # Running inside Docker container with full codebase mounted at /app
    cd /app
    PYTHONPATH=/app python -m pytest tests/ -v --tb=short --no-header 2>&1
  else
    # Running locally: resolve script location to find tests
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHONPATH="$SCRIPT_DIR" python -m pytest tests/ -v --tb=short --no-header 2>&1
  fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
