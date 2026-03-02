#!/bin/bash

# Read environment variables from metadata.json
GL_SERVER_DATA_PATH="$HOME/workspace/greenlight/.gltestserver"
GL_CA_CRT=$(jq -r '.ca_crt_path' ./metadata.json)
GL_NOBODY_CRT=$(jq -r '.nobody_crt_path' ./metadata.json)
GL_NOBODY_KEY=$(jq -r '.nobody_key_path' ./metadata.json)
GL_SCHEDULER_GRPC_URI=$(jq -r '.scheduler_grpc_uri' ./metadata.json)
GL_BITCOIN_RPC_URI=$(jq -r '.bitcoind_rpc_uri' ./metadata.json)
GL_GRPC_WEB_PROXY_URI=$(jq -r '.grpc_web_proxy_uri' ./metadata.json)
GL_GRPC_PORT=$(echo "$GL_GRPC_WEB_PROXY_URI" | sed -E 's/.*:([0-9]+)$/\1/')

RPC_USER=$(echo "$GL_BITCOIN_RPC_URI" | sed -E 's|^http://([^:]+):([^@]+)@([^:]+):([0-9]+)$|\1|')
RPC_PASS=$(echo "$GL_BITCOIN_RPC_URI" | sed -E 's|^http://([^:]+):([^@]+)@([^:]+):([0-9]+)$|\2|')
BITCOIN_HOST=$(echo "$GL_BITCOIN_RPC_URI" | sed -E 's|^http://([^:]+):([^@]+)@([^:]+):([0-9]+)$|\3|')
BITCOIN_PORT=$(echo "$GL_BITCOIN_RPC_URI" | sed -E 's|^http://([^:]+):([^@]+)@([^:]+):([0-9]+)$|\4|')
WALLET_NAME="testwallet"

LSP_DATA_DIR="$GL_SERVER_DATA_PATH/lsp"

# ── 1. Start the GL test server ───────────────────────────────────────────────
echo "Starting GL test server..."
gnome-terminal --title="GL Test Server" -- bash -c \
  "cd $HOME/workspace/greenlight && \
  uv run gltestserver run --directory=$GL_SERVER_DATA_PATH; \
  echo 'Press Enter to close...'; read"

sleep 5  # give the server a moment to come up

# ── 2. Register + schedule the LSP node ──────────────────────────────────────
echo "Registering LSP node..."
rm -rf "${LSP_DATA_DIR}" && mkdir -p "${LSP_DATA_DIR}"

gnome-terminal --title="Scheduler LSP" -- bash -c \
  "GL_CA_CRT=$GL_CA_CRT \
  GL_NOBODY_CRT=$GL_NOBODY_CRT \
  GL_NOBODY_KEY=$GL_NOBODY_KEY \
  GL_SCHEDULER_GRPC_URI=$GL_SCHEDULER_GRPC_URI \
  cargo run --bin glcli scheduler register \
    --network=regtest \
    --data-dir=${LSP_DATA_DIR} && sleep 1 && \
  GL_CA_CRT=$GL_CA_CRT \
  GL_NOBODY_CRT=$GL_NOBODY_CRT \
  GL_NOBODY_KEY=$GL_NOBODY_KEY \
  GL_SCHEDULER_GRPC_URI=$GL_SCHEDULER_GRPC_URI \
  cargo run --bin glcli scheduler schedule \
    --verbose \
    --network=regtest \
    --data-dir=${LSP_DATA_DIR}; \
  echo 'Press Enter to close...'; read"

# # ── 3. Start the signer for the LSP node ─────────────────────────────────────
# echo "Starting LSP signer..."
# gnome-terminal --title="Signer LSP" -- bash -c \
#   "GL_CA_CRT=$GL_CA_CRT \
#   GL_NOBODY_CRT=$GL_NOBODY_CRT \
#   GL_NOBODY_KEY=$GL_NOBODY_KEY \
#   GL_SCHEDULER_GRPC_URI=$GL_SCHEDULER_GRPC_URI \
#   cargo run --bin glcli signer run \
#     --verbose \
#     --network=regtest \
#     --data-dir=${LSP_DATA_DIR}; \
#   echo 'Press Enter to close...'; read"

# sleep 2

# # ── 4. Fund the LSP node ──────────────────────────────────────────────────────
# echo "Creating wallet and funding LSP node..."
# bitcoin-cli -rpcconnect="$BITCOIN_HOST" -rpcport="$BITCOIN_PORT" \
#   -rpcuser="$RPC_USER" -rpcpassword="$RPC_PASS" \
#   createwallet "$WALLET_NAME" > /dev/null

# bitcoin-cli -rpcconnect="$BITCOIN_HOST" -rpcport="$BITCOIN_PORT" \
#   -rpcuser="$RPC_USER" -rpcpassword="$RPC_PASS" \
#   -rpcwallet="$WALLET_NAME" -generate 101 > /dev/null

# # Replace with the LSP node's on-chain address
# LSP_ONCHAIN_ADDR="bcrt1q<YOUR_LSP_ADDRESS>"
# bitcoin-cli -rpcconnect="$BITCOIN_HOST" -rpcport="$BITCOIN_PORT" \
#   -rpcuser="$RPC_USER" -rpcpassword="$RPC_PASS" \
#   -rpcwallet="$WALLET_NAME" sendtoaddress "$LSP_ONCHAIN_ADDR" 1 > /dev/null

# bitcoin-cli -rpcconnect="$BITCOIN_HOST" -rpcport="$BITCOIN_PORT" \
#   -rpcuser="$RPC_USER" -rpcpassword="$RPC_PASS" \
#   -rpcwallet="$WALLET_NAME" -generate 6 > /dev/null

# echo "LSP node funded."

# # ── 5. Start the LSP server ───────────────────────────────────────────────────
# echo "Starting LSP server..."
# gnome-terminal --title="LSP Server" -- bash -c \
#   "GL_CA_CRT=$GL_CA_CRT \
#   GL_NOBODY_CRT=$GL_NOBODY_CRT \
#   GL_NOBODY_KEY=$GL_NOBODY_KEY \
#   GL_SCHEDULER_GRPC_URI=$GL_SCHEDULER_GRPC_URI \
#   GL_GRPC_WEB_PROXY_URI=$GL_GRPC_WEB_PROXY_URI \
#   cargo run --bin lsp_server \
#     --network=regtest \
#     --data-dir=${LSP_DATA_DIR}; \
#   echo 'Press Enter to close...'; read"

echo "All done. Test server + LSP server are running."
wait
