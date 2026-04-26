#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."

  # Determine working directory
  if [ -d "/eval_assets" ] && [ "$(pwd)" = "/eval_assets" ]; then
    APP_DIR="/eval_assets"
  else
    APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  fi

  # Copy codebase into eval_assets if running in container
  if [ -d "/app" ] && [ "$APP_DIR" = "/eval_assets" ]; then
    cp -a /app/. "$APP_DIR/" 2>/dev/null || true
  fi

  cd "$APP_DIR"

  SPRING_PID=""

  # Build and start Spring Boot if source exists
  if [ -f "pom.xml" ] && [ -d "src" ]; then
    echo "Building Spring Boot application..."
    mkdir -p data
    mvn clean package -q -DskipTests 2>/dev/null || mvn clean package -DskipTests 2>&1 | tail -20

    JAR=$(ls target/rentalyard-*.jar 2>/dev/null | head -1)
    if [ -n "$JAR" ]; then
      echo "Starting Spring Boot application..."
      java -Xms256m -Xmx512m -jar "$JAR" \
        --spring.datasource.url="jdbc:h2:file:./data/rentalyard" \
        --spring.jpa.open-in-view=false \
        > /tmp/spring_boot.log 2>&1 &
      SPRING_PID=$!

      echo "Waiting for application to start (up to 60 seconds)..."
      for i in $(seq 1 30); do
        if curl -sf http://localhost:8080/api/config/member-discount > /dev/null 2>&1; then
          echo "Application started after $((i * 2)) seconds"
          break
        fi
        sleep 2
      done
    else
      echo "Build succeeded but JAR not found"
    fi
  else
    echo "No source code found - running tests against (likely absent) server"
  fi

  # Run the test suite
  python3 "$APP_DIR/tests/run_tests.py" || true

  # Shut down Spring Boot
  if [ -n "$SPRING_PID" ]; then
    kill "$SPRING_PID" 2>/dev/null || true
    wait "$SPRING_PID" 2>/dev/null || true
  fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests
