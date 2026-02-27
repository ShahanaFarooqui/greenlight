#!/usr/bin/env bash
set -euo pipefail

# jest.setup.ts handles starting/stopping a fresh gltestserver around each test.
# This script just invokes Jest.
npx jest --verbose "$@"


# #!/usr/bin/env bash
# set -euo pipefail

# TESTSERVER_DIR="${GL_TESTSERVER_DIR:-/tmp/gltests}"
# METADATA="$TESTSERVER_DIR/metadata.json"

# # Clean stale metadata
# rm -f "$METADATA"
# mkdir -p "$TESTSERVER_DIR"

# # Start gltestserver in background
# uv run gltestserver run --directory="$TESTSERVER_DIR" &
# GLTESTSERVER_PID=$!

# # Wait for metadata.json to appear
# echo "Waiting for gltestserver to be ready..."
# TIMEOUT=120
# ELAPSED=0
# until [ -f "$METADATA" ]; do
#   sleep 0.5
#   ELAPSED=$((ELAPSED + 1))
#   if [ "$ELAPSED" -ge $((TIMEOUT * 2)) ]; then
#     echo "Timed out waiting for $METADATA" >&2
#     kill "$GLTESTSERVER_PID" 2>/dev/null
#     exit 1
#   fi
# done

# # Export GL_* vars from metadata into the current shell
# export GL_SCHEDULER_GRPC_URI=$(jq -r '.scheduler_grpc_uri' "$METADATA")
# export GL_CA_CRT=$(jq -r '.ca_crt_path' "$METADATA")
# export GL_NOBODY_CRT=$(jq -r '.nobody_crt_path' "$METADATA")
# export GL_NOBODY_KEY=$(jq -r '.nobody_key_path' "$METADATA")

# echo "✅ gltestserver ready: $GL_SCHEDULER_GRPC_URI"

# # Run Jest — env vars are now inherited by the Jest process
# npx jest --verbose "$@"
# EXIT_CODE=$?

# # Teardown
# kill "$GLTESTSERVER_PID" 2>/dev/null || true
# wait "$GLTESTSERVER_PID" 2>/dev/null || true
# rm -rf "$TESTSERVER_DIR"

# exit $EXIT_CODE
