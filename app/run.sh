#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e

# --- CONFIGURE THIS SECTION ---
run_all_tests() {
  echo "Running all tests..."
 
  JUNIT_JAR="/opt/junit-platform-console-standalone.jar"
  COMPILE_DIR="/tmp/compression_test_classes"
  REPORTS_DIR="/tmp/junit-reports"
  rm -rf "$COMPILE_DIR" "$REPORTS_DIR"
  mkdir -p "$COMPILE_DIR" "$REPORTS_DIR"
 
  # Locate test sources: prefer /eval_assets/tests, fall back to sibling tests/ directory
  if [ -d /eval_assets/tests ]; then
    TEST_SRC_DIR="/eval_assets/tests"
  else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    TEST_SRC_DIR="$SCRIPT_DIR/tests"
  fi
 
  # Compile implementation sources from codebase if present (failures tolerated)
  if [ -d /app/src/main/java ]; then
    find /app/src/main/java -name "*.java" > /tmp/src_files.txt 2>/dev/null || true
    if [ -s /tmp/src_files.txt ]; then
      javac -cp "$JUNIT_JAR" -d "$COMPILE_DIR" @/tmp/src_files.txt 2>&1 || true
    fi
  fi
 
  # Compile test sources against compiled implementation and JUnit
  find "$TEST_SRC_DIR" -name "*.java" > /tmp/test_files.txt 2>/dev/null || true
  if [ -s /tmp/test_files.txt ]; then
    javac -cp "$COMPILE_DIR:$JUNIT_JAR" -d "$COMPILE_DIR" @/tmp/test_files.txt 2>&1 || true
  fi
 
  # Run tests and generate XML reports
  java -jar "$JUNIT_JAR" \
    --class-path "$COMPILE_DIR" \
    --select-class CompressionLibraryTest \
    --details=verbose \
    --reports-dir="$REPORTS_DIR" 2>&1 || true
}
# --- END CONFIGURATION SECTION ---

### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests