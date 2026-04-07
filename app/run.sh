#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  if [ -d /eval_assets/tests ]; then
    # Running inside validation container: tests in /eval_assets, code in /app
    cd /eval_assets
    # Symlink /app/data into /eval_assets so tests resolve data/sample_data.csv
    # via their _PARENT_DIR-relative path without modifying test code
    [ ! -e /eval_assets/data ] && ln -sf /app/data /eval_assets/data || true
    PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header 2>&1 || true
  elif [ -d /app/tests ]; then
    # Running inside Docker container with full codebase mounted at /app
    cd /app
    python -m pytest tests/ -v --tb=short --no-header 2>&1 || true
  else
    # Running locally: use the directory containing this script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHON=$(command -v python 2>/dev/null || command -v python3)
    $PYTHON -m pytest tests/ -v --tb=short --no-header 2>&1 || true
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests