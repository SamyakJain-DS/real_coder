#!/bin/bash
### COMMON SETUP; DO NOT MODIFY ###
set -e
# --- CONFIGURE THIS SECTION ---
run_all_tests() {
    echo "Running all tests..."
 
    # ---- Locate the C# project directory --------------------------------
    # Check /app first (validation environment), then cwd (local environment).
    PROJECT_DIR="/app"
    for search_root in "/app" "$(pwd)"; do
        if [ -d "$search_root" ]; then
            found=$(find "$search_root" -maxdepth 6 -name "*.csproj" 2>/dev/null | head -1)
            if [ -n "$found" ]; then
                PROJECT_DIR="$(dirname "$found")"
                break
            fi
        fi
    done
 
    # ---- Start the ASP.NET Core server in the background ----------------
    ASPNETCORE_URLS="http://localhost:5000" dotnet run --project "$PROJECT_DIR" \
        >/dev/null 2>&1 &
    SERVER_PID=$!
 
    # ---- Wait up to 30 s for the server to accept connections -----------
    echo "Waiting for server..."
    for i in $(seq 1 15); do
        if python3 -c \
            "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/inventory', timeout=1)" \
            2>/dev/null; then
            echo "Server ready."
            break
        fi
        sleep 1
    done
 
    # ---- Run the test suite ---------------------------------------------
    if [ -d /eval_assets/tests ]; then
        cd /eval_assets
        python -m pytest tests/ -v --tb=short --no-header --color=no 2>&1
    elif [ -d /app/tests ]; then
        cd /app
        python -m pytest tests/ -v --tb=short --no-header --color=no 2>&1
    else
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$SCRIPT_DIR"
        PYTHON=$(command -v python 2>/dev/null || command -v python3)
        $PYTHON -m pytest tests/ -v --tb=short --no-header --color=no 2>&1
    fi
 
    # ---- Shut down the server -------------------------------------------
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
}
# --- END CONFIGURATION SECTION ---
### COMMON EXECUTION; DO NOT MODIFY ###
run_all_tests