#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..." >&2
 
  cd /app
 
  # If the project has a package.json, install deps, build, and start the preview server.
  # All setup output goes to stderr so stdout contains only the Playwright JSON.
  if [ -f package.json ]; then
    npm install >/dev/null 2>&1 || true
    npm run build >/dev/null 2>&1 || true
 
    npx vite preview --port 4173 >/dev/null 2>&1 &
    SERVER_PID=$!
 
    TRIES=0
    until (echo > /dev/tcp/localhost/4173) 2>/dev/null || [ "$TRIES" -ge 30 ]; do
      sleep 1
      TRIES=$((TRIES + 1))
    done
  fi
 
  # Locate the playwright config.
  # In validation: validation.sh unpacks tests.zip into /eval_assets, so config is at /eval_assets/tests/.
  # In local testing: the codebase dir is mounted at /app, so config is at /app/tests/.
  if [ -f /eval_assets/tests/playwright.config.js ]; then
    PW_CONFIG=/eval_assets/tests/playwright.config.js
    TESTS_DIR=/eval_assets/tests
  else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PW_CONFIG="${SCRIPT_DIR}/tests/playwright.config.js"
    TESTS_DIR="${SCRIPT_DIR}/tests"
  fi
 
  # Ensure the tests directory has a package.json that opts out of ESM mode.
  # Without this, a solution whose /app/package.json contains "type":"module"
  # causes Node to use ES module resolution for the test file, which does not
  # honour NODE_PATH — so `import { test, expect } from '@playwright/test'`
  # fails even though the package is installed globally.
  if [ ! -f "${TESTS_DIR}/package.json" ]; then
    echo '{"type":"commonjs"}' > "${TESTS_DIR}/package.json"
  fi
 
  export PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
  export NODE_PATH=/usr/lib/node_modules
 
  # Run tests. Playwright JSON (--reporter=json) goes to stdout → captured in
  # pw_output.json. Playwright's own diagnostic stderr is forwarded to this
  # script's stderr so it is visible in the caller's stderr capture — never
  # silently discarded.
  npx playwright test \
    --config "$PW_CONFIG" \
    --reporter=json \
    > /tmp/pw_output.json || true
 
  # If playwright produced no JSON output (crashed before writing), emit a
  # valid but empty structure so parsing.py never sees an empty file.
  if [ ! -s /tmp/pw_output.json ]; then
    echo '{"suites":[],"errors":[],"stats":{}}' > /tmp/pw_output.json
  fi
 
  cat /tmp/pw_output.json
 
  # Shut down the preview server if one was started.
  if [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests