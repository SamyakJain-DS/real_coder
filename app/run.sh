#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
  # Determine where the tests directory lives.
  # In the Docker evaluation environment, tests are extracted to /eval_assets/tests/
  # and the codebase under test lives in /app/.
  # For local development the tests live alongside this script.
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
 
  if [ -d /eval_assets/tests ]; then
    # Docker evaluation environment: tests in /eval_assets, code in /app.
    #
    # Tests compute _ROOT_DIR = /eval_assets/ (one level above the tests/ dir)
    # and expect vault.py and data/ to be present there via path-based lookups
    # (os.path.join, subprocess path, etc). PYTHONPATH=/app handles Python
    # imports but not direct path references, so we create symlinks.
    ln -sf /app/vault.py /eval_assets/vault.py 2>/dev/null || true
    ln -sf /app/data     /eval_assets/data     2>/dev/null || true
    # -n auto: use all available CPU cores for parallel execution
    # --dist loadscope: group tests by class into workers — critical for
    #   TestIdleTimeout which shares a session file across its subprocess calls
    PYTHONPATH=/app:${PYTHONPATH:-} python -m pytest /eval_assets/tests/ -v --tb=short --no-header -n auto --dist loadscope 2>&1
  elif [ -d "${SCRIPT_DIR}/tests" ]; then
    # Local development: tests are next to this script
    PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH:-}" python -m pytest "${SCRIPT_DIR}/tests/" -v --tb=short --no-header -n auto --dist loadscope 2>&1
  else
    echo "ERROR: Could not locate tests directory." >&2
    exit 1
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests