#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
 
  if [ -d /eval_assets/tests ]; then
    # Sandbox: tests live in /eval_assets/tests, Go source lives in /app.
    # The test file resolves _PARENT_DIR as one level above the test directory
    # (/eval_assets), then runs `go build .` with cwd=/eval_assets.
    # Copy Go source files and module manifests into /eval_assets so the build works.
    find /app -maxdepth 1 -name "*.go" -exec cp {} /eval_assets/ \; 2>/dev/null || true
    cp /app/go.mod /eval_assets/ 2>/dev/null || true
    cp /app/go.sum /eval_assets/ 2>/dev/null || true
    cd /eval_assets
    python -m pytest tests/ -v --tb=short --no-header 2>&1
 
  elif [ -d /app/tests ]; then
    # Docker container with full codebase mounted at /app
    cd /app
    python -m pytest tests/ -v --tb=short --no-header 2>&1
 
  else
    # Local development: run from the directory containing this script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHON=$(command -v python3 2>/dev/null || command -v python)
    $PYTHON -m pytest tests/ -v --tb=short --no-header 2>&1
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests