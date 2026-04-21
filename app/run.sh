#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."

  # If tests were unzipped flat under /eval_assets (no tests/ subdir),
  # normalize into /eval_assets/tests/ so that relative imports of the
  # form `../printManager.js` from a test file still resolve correctly.
  if ls /eval_assets/test_*.mjs >/dev/null 2>&1 && [ ! -d /eval_assets/tests ]; then
    mkdir -p /eval_assets/tests
    mv /eval_assets/test_*.mjs /eval_assets/tests/ 2>/dev/null || true
    [ -f /eval_assets/package.json ] && mv /eval_assets/package.json /eval_assets/tests/ 2>/dev/null || true
    [ -f /eval_assets/package-lock.json ] && mv /eval_assets/package-lock.json /eval_assets/tests/ 2>/dev/null || true
  fi

  # Pick the tests directory. Validation populates /eval_assets; local
  # runs (with only the codebase mounted) fall back to /app/tests.
  local tests_dir=""
  if [ -d /eval_assets/tests ]; then
    tests_dir=/eval_assets/tests
    # Place the agent's JS source files one directory above the tests
    # so `new URL('../printManager.js', import.meta.url)` resolves.
    find /app -maxdepth 1 -name "*.js" -exec cp {} /eval_assets/ \; 2>/dev/null || true
  elif [ -d /app/tests ]; then
    tests_dir=/app/tests
  else
    echo "No tests directory found (looked in /eval_assets/tests and /app/tests)." >&2
    return 0
  fi

  # Expose pre-installed jsdom to the test suite without any runtime install.
  if [ ! -d "${tests_dir}/node_modules" ] && [ -d /deps/node_modules ]; then
    cp -r /deps/node_modules "${tests_dir}/node_modules" 2>/dev/null || true
  fi

  # Run every discovered test file with Node's built-in test runner.
  # The `|| true` guarantees a non-zero test exit code does not abort run.sh.
  (
    cd "$tests_dir"
    if ls test_*.mjs >/dev/null 2>&1; then
      node --test test_*.mjs
    else
      echo "No test files matching test_*.mjs were found in $tests_dir." >&2
    fi
  ) || true
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
