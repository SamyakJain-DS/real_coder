#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."

  if [ -d /eval_assets/tests ]; then
    cd /eval_assets
    PYTHONPATH=/app:/eval_assets:${PYTHONPATH:-} python3 -m pytest tests/ -v --tb=short --no-header 2>&1
  else
    cd /app
    PYTHONPATH=/app:${PYTHONPATH:-} python3 -m pytest tests/ -v --tb=short --no-header 2>&1
  fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests