#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
# Replace this with your command to run all tests
run_all_tests() {
  echo "Running all tests..."
  if [ -d /eval_assets/tests ]; then
    # Running inside the validation container: tests live in /eval_assets,
    # codebase (optimize_images.py) lives in /app.
    cd /eval_assets
    PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header 2>&1
  elif [ -d /app/tests ]; then
    # Running inside a local Docker container with codebase mounted at /app.
    cd /app
    python -m pytest tests/ -v --tb=short --no-header 2>&1
  else
    # Running directly on the host (e.g. from /codebase).
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHON=$(command -v python 2>/dev/null || command -v python3)
    $PYTHON -m pytest tests/ -v --tb=short --no-header 2>&1
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests