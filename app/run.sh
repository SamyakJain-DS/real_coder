#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        cd /app
        python -m pytest /eval_assets/tests/ -v --tb=short --no-header --color=no -p no:cacheprovider
    else
        cd /app
        python -m pytest tests/ -v --tb=short --no-header --color=no -p no:cacheprovider
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests