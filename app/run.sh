#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
 
    # ----------------------------------------------------------------
    # Locate the test file.
    # ----------------------------------------------------------------
    TEST_FILE=""
    for candidate in \
        "/eval_assets/tests/test_aco_mssp.py" \
        "/eval_assets/test_aco_mssp.py" \
        "/app/tests/test_aco_mssp.py"; do
        if [ -f "$candidate" ]; then
            TEST_FILE="$candidate"
            echo "[run.sh] Test file found: $TEST_FILE"
            break
        fi
    done
 
    if [ -z "$TEST_FILE" ]; then
        echo "[run.sh] ERROR: test_aco_mssp.py not found in any expected location." >&2
        echo "[run.sh]   Searched: /eval_assets/tests/test_aco_mssp.py" >&2
        echo "[run.sh]            /eval_assets/test_aco_mssp.py" >&2
        echo "[run.sh]            /app/tests/test_aco_mssp.py" >&2
        exit 1
    fi
 
    # ----------------------------------------------------------------
    # If the agent's codebase is present, build it and start the server.
    # An empty repo has no Aco.Mssp.sln, so this block is skipped and
    # pytest falls through to its graceful-fail path (all FAILED).
    # ----------------------------------------------------------------
    SERVER_PID=""
 
    if [ -f "/app/Aco.Mssp.sln" ]; then
        echo "[run.sh] Aco.Mssp.sln found - building the .NET project..."
        cd /app
 
        BUILD_EXIT=0
        dotnet build Aco.Mssp.sln --configuration Release --nologo 2>&1 \
            || BUILD_EXIT=$?
 
        if [ "$BUILD_EXIT" -eq 0 ]; then
            echo "[run.sh] Build succeeded - starting ASP.NET Core server on port 5000..."
 
            # Tell ASP.NET Core to listen on HTTP port 5000 (no HTTPS redirect)
            export ASPNETCORE_URLS="http://0.0.0.0:5000"
            export ASPNETCORE_ENVIRONMENT="Development"
 
            dotnet run \
                --project Aco.Mssp.Api \
                --configuration Release \
                --no-build \
                2>&1 &
            SERVER_PID=$!
 
            echo "[run.sh] Waiting for server to be ready (up to 120 s)..."
            READY=0
            for i in $(seq 1 120); do
                # curl exits 0 on any HTTP response; non-zero only on connection failure
                if curl -s http://localhost:5000/ -o /dev/null 2>/dev/null; then
                    echo "[run.sh] Server is ready (${i}s elapsed)."
                    READY=1
                    break
                fi
                sleep 1
            done
 
            if [ "$READY" -eq 0 ]; then
                echo "[run.sh] WARNING: server did not become ready within 120 s." \
                     "Tests will run but are likely to fail."
            fi
        else
            echo "[run.sh] Build failed (exit $BUILD_EXIT) - tests will run without a server."
        fi
 
        # Return to a neutral directory; /eval_assets always exists (created in Dockerfile)
        cd /eval_assets
    else
        echo "[run.sh] No Aco.Mssp.sln in /app - running tests against empty repository."
    fi
 
    # ----------------------------------------------------------------
    # Run the pytest suite against whichever test file was found.
    # The || true prevents set -e from aborting the script on failures.
    # ACO_BASE_URL matches the default used inside test_aco_mssp.py.
    # ----------------------------------------------------------------
    export ACO_BASE_URL="http://localhost:5000"
    python3 -m pytest "$TEST_FILE" \
        -v --tb=short --no-header \
        2>&1 || true
 
    # ----------------------------------------------------------------
    # Graceful cleanup - stop the background server if we started one.
    # ----------------------------------------------------------------
    if [ -n "$SERVER_PID" ]; then
        echo "[run.sh] Stopping server (PID $SERVER_PID)..."
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests