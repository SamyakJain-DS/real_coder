#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..." >&2
 
  SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
  SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
 
  # When invoked from the sandbox (/eval_assets or /usr/local/bin), the
  # codebase under test lives in /app; otherwise use the script's own dir.
  if [ "$SCRIPT_DIR" = "/eval_assets" ] || [ "$SCRIPT_DIR" = "/usr/local/bin" ]; then
    CODEBASE_DIR="/app"
  else
    CODEBASE_DIR="$SCRIPT_DIR"
  fi
 
  # Find the tests directory.
  TEST_DIR=""
  for candidate in "$SCRIPT_DIR/tests" "/eval_assets/tests"; do
    if [ -d "$candidate" ]; then
      TEST_DIR="$candidate"
      break
    fi
  done
 
  # The asset root is the parent directory of tests/.
  TEST_ASSET_ROOT="$SCRIPT_DIR"
  if [ -n "$TEST_DIR" ]; then
    TEST_ASSET_ROOT="$(cd "$TEST_DIR/.." && pwd)"
  fi
 
  # Symlink /deps/node_modules into tests/ so Vitest and all pre-installed
  # packages are resolvable by Node's module resolution from the test files.
  if [ -n "$TEST_DIR" ] && [ ! -e "$TEST_DIR/node_modules" ] && [ -d "/deps/node_modules" ]; then
    ln -s /deps/node_modules "$TEST_DIR/node_modules" 2>/dev/null || true
  fi
 
  # Symlink the codebase's src/ into the asset root so the relative import
  # '../src/index' used by tests resolves to the implementation under test.
  #
  # On an empty repo (no src/ present), the link is removed rather than
  # replaced with stub files. The test helpers already handle a missing
  # module gracefully: loadModule() catches the import error and returns
  # null, causing every test to report FAILED (not ERRORED). This satisfies
  # the Fail-to-Pass baseline requirement without any stub fabrication.
  TEST_SOURCE_LINK="$TEST_ASSET_ROOT/src"
  if [ -d "$CODEBASE_DIR/src" ]; then
    if [ "$CODEBASE_DIR/src" != "$TEST_SOURCE_LINK" ]; then
      rm -rf "$TEST_SOURCE_LINK" 2>/dev/null || true
      ln -s "$CODEBASE_DIR/src" "$TEST_SOURCE_LINK" 2>/dev/null || true
    fi
  else
    # No src/ — ensure the stale link (if any) is removed.
    rm -rf "$TEST_SOURCE_LINK" 2>/dev/null || true
  fi
 
  # Mirror the codebase's package.json one level above tests/ so tests that
  # walk upward searching for it (e.g., the ESM format check in AS3) find it.
  TEST_PKG_LINK="$TEST_ASSET_ROOT/package.json"
  if [ -f "$CODEBASE_DIR/package.json" ] && [ "$CODEBASE_DIR/package.json" != "$TEST_PKG_LINK" ]; then
    if [ ! -e "$TEST_PKG_LINK" ] || [ -L "$TEST_PKG_LINK" ]; then
      rm -f "$TEST_PKG_LINK" 2>/dev/null || true
      ln -s "$CODEBASE_DIR/package.json" "$TEST_PKG_LINK" 2>/dev/null \
        || cp "$CODEBASE_DIR/package.json" "$TEST_PKG_LINK" 2>/dev/null \
        || true
    fi
  fi
 
  # Find the first available node_modules directory and expose it via
  # NODE_PATH so imports from src/ (outside the tests/ tree) resolve correctly.
  NODE_MODULES_DIR=""
  for candidate in \
      "$TEST_DIR/node_modules" \
      "$CODEBASE_DIR/node_modules" \
      "/deps/node_modules"; do
    if [ -d "$candidate" ]; then
      NODE_MODULES_DIR="$candidate"
      break
    fi
  done
 
  if [ -n "$NODE_MODULES_DIR" ]; then
    export NODE_PATH="$NODE_MODULES_DIR${NODE_PATH:+:$NODE_PATH}"
    export PATH="$NODE_MODULES_DIR/.bin:$PATH"
  fi
 
  # Find the Vitest binary.
  VITEST_BIN=""
  for candidate in \
      "$NODE_MODULES_DIR/.bin/vitest" \
      "$TEST_DIR/node_modules/.bin/vitest" \
      "$CODEBASE_DIR/node_modules/.bin/vitest" \
      "/deps/node_modules/.bin/vitest"; do
    if [ -x "$candidate" ]; then
      VITEST_BIN="$candidate"
      break
    fi
  done
  if [ -z "$VITEST_BIN" ] && command -v vitest >/dev/null 2>&1; then
    VITEST_BIN="$(command -v vitest)"
  fi
 
  # Find the Vitest config file.
  VITEST_CONFIG=""
  for candidate in \
      "$TEST_DIR/vitest.config.ts" \
      "$CODEBASE_DIR/vitest.config.ts"; do
    if [ -f "$candidate" ]; then
      VITEST_CONFIG="$candidate"
      break
    fi
  done
 
  if [ -z "$TEST_DIR" ]; then
    echo "ERROR: tests directory not found." >&2
    return 1
  fi
  if [ -z "$VITEST_BIN" ]; then
    echo "ERROR: vitest binary not found." >&2
    return 1
  fi
 
  # Run Vitest. The || true prevents set -e from aborting the script when
  # tests fail (non-zero exit from vitest is expected on the baseline run).
  (
    cd "$TEST_ASSET_ROOT"
    if [ -n "$VITEST_CONFIG" ]; then
      "$VITEST_BIN" run --config "$VITEST_CONFIG" --reporter=verbose
    else
      "$VITEST_BIN" run --reporter=verbose
    fi
  ) || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests