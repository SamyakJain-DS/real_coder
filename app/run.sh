#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  if [ -d /eval_assets/tests ]; then
    # Running inside validation container: tests in /eval_assets, code in /app
    cd /eval_assets
    # CLI subprocess tests resolve scripts relative to the test file's parent directory
    # (/eval_assets/), so symlink app Python scripts here so they can be found.
    for f in /app/*.py; do
      [ -f "$f" ] && ln -sf "$f" "/eval_assets/$(basename "$f")" 2>/dev/null || true
    done
    PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest tests/ -v --tb=short --no-header
  elif [ -d /app/tests ]; then
    # Running inside Docker container with full codebase mounted at /app
    cd /app
    python -m pytest tests/ -v --tb=short --no-header
  else
    # Running locally: use the directory containing this script
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    PYTHON=$(command -v python 2>/dev/null || command -v python3)
    $PYTHON -m pytest tests/ -v --tb=short --no-header
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests