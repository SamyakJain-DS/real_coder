#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
# Run the pytest suite against the Maven/Spring project in /app.
run_all_tests() {
  echo "Running all tests..."
 
  # Copy test files from /eval_assets into /app so pytest can discover them.
  # Using the trailing /. syntax copies the CONTENTS of the source directory,
  # which avoids a nesting bug when the destination already exists on a second run.
  if [ -d /eval_assets/tests ]; then
    mkdir -p /app/tests
    cp -rp /eval_assets/tests/. /app/tests/
  fi
 
  # If the submitted codebase contains a Maven project, start the Spring Boot
  # server before running tests.  The test fixture requires a live server;
  # without one, every test fails (correct "before" behaviour).
  #
  # The server is started here rather than inside the pytest fixture so there
  # is no fixed startup timeout — the wait loop below runs for up to 5 minutes,
  # accommodating both cold Maven caches and slow build environments.
  # SPRING_BASE_URL is exported so the fixture skips its own server startup.
  if [ -f /app/pom.xml ]; then
    SPRING_PORT=$(python3 -c "
import socket
s = socket.socket()
s.bind(('127.0.0.1', 0))
p = s.getsockname()[1]
s.close()
print(p)
")
    export SPRING_PORT
    export SPRING_BASE_URL="http://127.0.0.1:$SPRING_PORT"
 
    # setsid puts Maven and the Spring Boot JVM it forks into a new process
    # group so both are killed together when the script exits.
    echo "Starting Spring Boot server on port $SPRING_PORT..."
    setsid mvn -q spring-boot:run \
      "-Dspring-boot.run.arguments=--server.port=$SPRING_PORT" \
      -f /app/pom.xml \
      > /dev/null 2>&1 &
    SPRING_PID=$!
 
    # shellcheck disable=SC2064
    trap "kill -- -$SPRING_PID 2>/dev/null || true" EXIT
 
    # Poll until the server responds or the 5-minute deadline passes.
    python3 -c "
import os, sys, time
from urllib.request import urlopen
from urllib.error import HTTPError
 
url = 'http://127.0.0.1:' + os.environ['SPRING_PORT'] + '/api/commissions/-1'
deadline = time.time() + 300
while time.time() < deadline:
    try:
        urlopen(url, timeout=2)
        print('Server is ready.')
        sys.exit(0)
    except HTTPError:
        print('Server is ready.')
        sys.exit(0)
    except Exception:
        time.sleep(1)
print('WARNING: server did not become reachable within 5 minutes.')
" || true
  fi
 
  cd /app
  PYTHONPATH=/app/tests:${PYTHONPATH:-} python3 -m pytest tests/ -v --tb=short --no-header 2>&1
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests