#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  if [ -d /eval_assets ] && find /eval_assets -name 'test_*.py' | grep -q .; then
    cd /app && python -m pytest /eval_assets/ -v --tb=short --no-header 2>&1 | tee /tmp/test_stdout.txt
  else
    cd /app && python -m pytest tests/ -v --tb=short --no-header 2>&1 | tee /tmp/test_stdout.txt
  fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests