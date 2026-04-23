#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  cd "$(dirname "$(readlink -f "$0")")"
  PYTHONPATH=/app python3 -m pytest tests/test_tripwire.py -v --tb=short --no-header 2>&1
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
