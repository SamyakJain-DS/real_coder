#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."

  # Resolve the codebase location. Supports Docker (/app) and local layouts.
  if [[ -f "/app/package.json" ]]; then
    APP_DIR="/app"
  elif [[ -f "package.json" ]]; then
    APP_DIR="$PWD"
  else
    APP_DIR=""
  fi

  SERVER_PID=""

  # When a codebase is present, install dependencies and pre-start the
  # backend. The ts-node startup on a WSL/bind-mount filesystem can take
  # tens of seconds; pytest's own conftest has a shorter ready-poll that
  # times out before the server is up, so we boot it here and wait long
  # enough for it to be reachable. conftest.py detects an already-running
  # server and skips its own launch. When no codebase is present (baseline
  # run against an empty /app), skip startup so the tests fail cleanly
  # with "Server is not reachable on localhost:3000".
  if [[ -n "$APP_DIR" ]]; then
    if [[ ! -d "$APP_DIR/node_modules" ]]; then
      echo "Installing npm dependencies..."
      (cd "$APP_DIR" && npm install --quiet --no-audit --no-fund 2>&1 | tail -5)
    fi

    if [[ -f "$APP_DIR/src/server.ts" ]]; then
      # Remove any stale SQLite file left over from a prior run so the
      # server re-seeds a clean database. This matters when the codebase
      # directory is bind-mounted from the host (local dev), where the
      # data file would otherwise persist across invocations and pollute
      # confirmed-booking state between test runs.
      rm -f "$APP_DIR/adventure.db" "$APP_DIR/adventure.db-journal" \
            "$APP_DIR/adventure.db-wal" "$APP_DIR/adventure.db-shm" 2>/dev/null || true

      echo "Starting backend server..."
      (
        cd "$APP_DIR"
        TS_NODE_TRANSPILE_ONLY=true \
          ts-node src/server.ts \
          > /tmp/server.log 2>&1
      ) &
      SERVER_PID=$!

      # Poll until the API answers, up to ~90 seconds.
      for _ in $(seq 1 180); do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/trips \
             | grep -qE "^[12345][0-9][0-9]$"; then
          echo "Backend server is ready."
          break
        fi
        if ! kill -0 "$SERVER_PID" 2>/dev/null; then
          echo "Backend server exited early. Log tail:"
          tail -30 /tmp/server.log || true
          break
        fi
        sleep 0.5
      done
    fi
  fi

  # Locate the test file - supports both Docker (/eval_assets) and local layouts
  if [[ -f "/eval_assets/tests/test_requirements.py" ]]; then
    TEST_FILE="/eval_assets/tests/test_requirements.py"
  else
    TEST_FILE="tests/test_requirements.py"
  fi

  python3 -m pytest -vv "$TEST_FILE" --no-header -p no:cacheprovider || true

  if [[ -n "$SERVER_PID" ]]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests