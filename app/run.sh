#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
    echo "Running all tests..."
    if [ -d /eval_assets/tests ]; then
        # Running inside validation container: tests in /eval_assets; code in /app
        cd /eval_assets
        /node_modules/.bin/vitest run --config tests/vitest.config.ts --reporter=verbose --reporter=json
    elif [ -d /app/tests ]; then
        # Running inside Docker container with full codebase mounted at /app.
        # Copy tests alongside node_modules so vitest can resolve packages via
        # standard Node module lookup (walking up from /eval_assets/tests/ to
        # /eval_assets/node_modules/). This mirrors the validation container layout.
        cp -r /app/tests /eval_assets/tests
        cd /eval_assets
        /node_modules/.bin/vitest run --config tests/vitest.config.ts --reporter=verbose --reporter=json
    else
        echo "No test directory found" >&2
        exit 1
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests