"""
Jest Global Setup Script — RPC Server Mode
==========================================
Spins up a full test network and then runs an HTTP/JSON-RPC server so that
Jest tests can call into Python to:
  - create new CLN nodes  (nf.get_node)
  - create new GL clients (clients.new)
  - register a GL client
  - get a GL node handle
  - connect peers
  - fund wallets / channels
  - mine blocks

Lifecycle
---------
  globalSetup.ts   →  spawns this script, waits for /tmp/jest-gl-network.json
  Jest tests       →  call NetworkClient.ts helpers (HTTP POST to RPC server)
  globalTeardown.ts → POST /shutdown  (or kill via PID file)

Usage
-----
  uv run python3 setup_network.py            # start server
  uv run python3 setup_network.py --teardown # kill via PID file
"""

import sys
import os
import json
import signal
import argparse
import tempfile
import logging
import threading
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from decimal import Decimal

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger("setup_network")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GREENLIGHT_ROOT = Path(os.environ.get("GREENLIGHT_ROOT", Path.home() / "workspace" / "greenlight"))
GL_TESTING_PATH = GREENLIGHT_ROOT / "libs" / "gl-testing"
GL_CLIENT_PATH  = GREENLIGHT_ROOT / "libs" / "gl-client-py"

for p in [str(GL_TESTING_PATH), str(GL_CLIENT_PATH)]:
    if p not in sys.path:
        sys.path.insert(0, p)

OUTPUT_JSON = Path("/tmp/jest-gl-network.json")
PIDS_FILE   = Path("/tmp/jest-gl-network.pids")
RPC_PORT    = int(os.environ.get("JEST_NETWORK_RPC_PORT", "19876"))

CERT_DIR = Path(tempfile.mkdtemp(prefix="jest-gl-certs-"))
NODE_DIR = Path(tempfile.mkdtemp(prefix="jest-gl-nodes-"))

# ---------------------------------------------------------------------------
# Global state — populated during setup(), shared with RPC handlers
# ---------------------------------------------------------------------------
STATE = {
    "bitcoind":   None,
    "scheduler":  None,
    "nf":         None,  # GlNodeFactory
    "clients":    None,  # Clients fixture
    "node_dir":   None,
    "nodes":      {},    # name -> LightningNode
    "gl_clients": {},    # name -> Client
    "gl_nodes":   {},    # name -> GL node handle (stored after first c.node() call)
}

_shutdown_event = threading.Event()


# ---------------------------------------------------------------------------
# Teardown helper
# ---------------------------------------------------------------------------
def teardown():
    if not PIDS_FILE.exists():
        logger.info("No PID file found, nothing to tear down.")
        return
    pids = json.loads(PIDS_FILE.read_text())
    for name, pid in pids.items():
        try:
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Killed {name} (pid={pid})")
        except ProcessLookupError:
            logger.info(f"{name} (pid={pid}) already gone")
        except Exception as e:
            logger.warning(f"Could not kill {name} (pid={pid}): {e}")
    PIDS_FILE.unlink(missing_ok=True)
    OUTPUT_JSON.unlink(missing_ok=True)
    logger.info("Teardown complete.")


# ---------------------------------------------------------------------------
# RPC method implementations
# ---------------------------------------------------------------------------
def rpc_get_node(params: dict) -> dict:
    """Create a new CLN node via nf.get_node(). Stores and returns node info."""
    options = params.get("options", {"disable-plugin": "cln-grpc"})
    node = STATE["nf"].get_node(options=options)
    name = f"node-{node.info['id'][:8]}"
    STATE["nodes"][name] = node
    logger.info(f"Created CLN node {name}")
    return {
        "name":     name,
        "id":       node.info["id"],
        "rpc_path": str(Path(STATE["node_dir"]) / node.daemon.lightning_dir / "regtest" / "lightning-rpc"),
        "p2p_addr": f"127.0.0.1:{node.daemon.port}",
    }


def rpc_connect_peer(params: dict) -> dict:
    """Connect a stored GL node handle to a peer."""
    name      = params["name"]
    peer_id   = params["peer_id"]
    peer_addr = params["peer_addr"]
    gl1 = STATE["gl_nodes"][name]
    gl1.connect_peer(peer_id, peer_addr)
    logger.info(f"GL node {name} connected to {peer_id}")
    return {"ok": True}


def rpc_fund_wallet(params: dict) -> dict:
    """Send on-chain funds to a GL node's bech32 address and wait for confirmation."""
    from pyln.testing.utils import wait_for
    name = params["name"]
    sats = params.get("sats", 10_000_000)
    gl1  = STATE["gl_nodes"][name]
    addr = gl1.new_address().bech32
    STATE["bitcoind"].rpc.sendtoaddress(addr, sats / 1e8)
    STATE["bitcoind"].generate_block(1, wait_for_mempool=1)
    wait_for(lambda: len(gl1.list_funds().outputs) > 0)
    logger.info(f"Funded GL node {name} with {sats} sats")
    return {"address": addr, "sats": sats}


def rpc_generate_block(params: dict) -> dict:
    """Mine blocks on bitcoind."""
    n                = params.get("numblocks", 1)
    wait_for_mempool = params.get("wait_for_mempool", 0)
    STATE["bitcoind"].generate_block(n, wait_for_mempool=wait_for_mempool)
    logger.info(f"Mined {n} block(s)")
    return {"blocks": n}


def rpc_list_datastore(params: dict) -> dict:
    """Call gl1.list_datastore(key=[...]) on a stored GL node handle."""
    name = params["name"]
    key  = params.get("key", [])
    gl1  = STATE["gl_nodes"][name]
    res  = gl1.list_datastore(key=key)
    return {
        "datastore": [
            {"key": list(e.key), "string": e.string, "generation": e.generation}
            for e in res.datastore
        ]
    }


def rpc_shutdown(_params: dict) -> dict:
    logger.info("Shutdown requested via RPC.")
    _shutdown_event.set()
    return {"ok": True}


RPC_METHODS = {
    "get_node":        rpc_get_node,
    "connect_peer":    rpc_connect_peer,
    "fund_wallet":     rpc_fund_wallet,
    "generate_block":  rpc_generate_block,
    "list_datastore":  rpc_list_datastore,
    "shutdown":        rpc_shutdown,
}


# ---------------------------------------------------------------------------
# HTTP/JSON-RPC server
# ---------------------------------------------------------------------------
class RPCHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logger.debug(f"HTTP {fmt}", *args)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        try:
            req    = json.loads(body)
            method = req.get("method")
            params = req.get("params", {})
            if method not in RPC_METHODS:
                raise ValueError(f"Unknown method: {method}")
            result = RPC_METHODS[method](params)
            self._respond(200, {"result": result})
        except Exception as e:
            logger.error(traceback.format_exc())
            self._respond(500, {"error": str(e)})

    def _respond(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
def setup():
    from ephemeral_port_reserve import reserve
    from pyln.testing.utils import BitcoinD, BITCOIND_CONFIG
    from gltesting import certs
    from gltesting.scheduler import Scheduler
    from gltesting.identity import Identity
    from gltesting.network import GlNodeFactory
    from clnvm import ClnVersionManager
    import concurrent.futures
    from pyln.testing.db import SqliteDbProvider
    from pyln.testing.utils import LightningNode

    pids = {}

    # ------------------------------------------------------------------
    # 1. Certs
    # ------------------------------------------------------------------
    logger.info(f"Cert directory: {CERT_DIR}")
    os.environ["GL_CERT_PATH"] = str(CERT_DIR)
    os.environ["GL_CA_CRT"]    = str(CERT_DIR / "ca.pem")

    certs.genca("/")
    certs.genca("/services")
    certs.gencert("/services/scheduler")
    certs.genca("/users")
    certs.gencert("/users/nobody")

    os.environ["GL_NOBODY_CRT"] = str(CERT_DIR / "users" / "nobody.crt")
    os.environ["GL_NOBODY_KEY"] = str(CERT_DIR / "users" / "nobody-key.pem")
    logger.info("Certificates generated.")

    # ------------------------------------------------------------------
    # 2. bitcoind
    # ------------------------------------------------------------------
    bitcoin_dir = NODE_DIR / "bitcoind"
    bitcoin_dir.mkdir(parents=True, exist_ok=True)
    bitcoind = BitcoinD(bitcoin_dir=str(bitcoin_dir))
    bitcoind.start()
    pids["bitcoind"] = bitcoind.proc.pid
    STATE["bitcoind"] = bitcoind
    logger.info(f"bitcoind started (pid={bitcoind.proc.pid})")

    # ------------------------------------------------------------------
    # 3. Scheduler
    # ------------------------------------------------------------------
    btcproxy = bitcoind.get_proxy()
    feerates  = (15000, 11000, 7500, 3750)

    def mock_estimatesmartfee(r):
        mapping = {
            (2,   "CONSERVATIVE"): feerates[0] * 4,
            (6,   "ECONOMICAL"):   feerates[1] * 4,
            (12,  "ECONOMICAL"):   feerates[2] * 4,
            (100, "ECONOMICAL"):   feerates[3] * 4,
        }
        feerate = mapping.get(tuple(r["params"]), 42)
        return {"id": r["id"], "error": None,
                "result": {"feerate": Decimal(feerate) / 10**8}}

    btcproxy.mock_rpc("estimatesmartfee", mock_estimatesmartfee)

    scheduler = Scheduler(
        bitcoind=btcproxy,
        grpc_port=reserve(),
        identity=Identity.from_path("/services/scheduler"),
    )
    scheduler.start()
    os.environ["GL_SCHEDULER_GRPC_URI"] = scheduler.grpc_addr
    STATE["scheduler"] = scheduler
    logger.info(f"Scheduler at {scheduler.grpc_addr}")

    # ------------------------------------------------------------------
    # 4. CLN version
    # ------------------------------------------------------------------
    manager = ClnVersionManager()
    latest  = manager.latest()
    os.environ["PATH"] += f":{latest.bin_path}"
    logger.info(f"CLN version: {latest}")

    # ------------------------------------------------------------------
    # 5. Node factory + Clients
    # ------------------------------------------------------------------
    node_dir = NODE_DIR / "nodes"
    node_dir.mkdir(parents=True, exist_ok=True)
    STATE["node_dir"] = str(node_dir)

    class FakeNode:
        def get_closest_marker(self, _): return None
        def get_marker(self, _):         return None

    class FakeConfig:
        @staticmethod
        def get_terminal_writer(): return None
        def getoption(self, _, default=None): return default
        def getini(self, _): return []

    class FakeRequest:
        node   = FakeNode()
        config = FakeConfig()
        def addfinalizer(self, _): pass

    executor    = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    db_provider = SqliteDbProvider(str(node_dir))
    db_provider.start()

    nf = GlNodeFactory(
        FakeRequest(), "jest-setup", bitcoind, executor,
        directory=str(node_dir), db_provider=db_provider,
        node_cls=LightningNode, jsonschemas={},
    )
    STATE["nf"]      = nf
    logger.info("NodeFactory and Clients ready.")

    # ------------------------------------------------------------------
    # 6. Mine initial blocks for coinbase maturity
    # ------------------------------------------------------------------
    bitcoind.generate_block(101)
    logger.info("Mined 101 blocks for coinbase maturity.")

    # ------------------------------------------------------------------
    # 7. Write output JSON for Jest globalSetup to detect readiness
    # ------------------------------------------------------------------
    output = {
        "rpc_url":            f"http://127.0.0.1:{RPC_PORT}",
        "scheduler_grpc_uri": scheduler.grpc_addr,
        "ca_crt_path":        str(CERT_DIR / "ca.pem"),
        "nobody_crt_path":    str(CERT_DIR / "users" / "nobody.crt"),
        "nobody_key_path":    str(CERT_DIR / "users" / "nobody-key.pem"),
        "cert_path":          str(CERT_DIR),
        "bitcoind_rpc_uri":   f"http://rpcuser:rpcpass@localhost:{bitcoind.rpcport}",
        "bitcoind_rpc_port":  bitcoind.rpcport,
    }
    OUTPUT_JSON.write_text(json.dumps(output, indent=2))
    logger.info(f"Network config written to {OUTPUT_JSON}")

    # ------------------------------------------------------------------
    # 8. PID file
    # ------------------------------------------------------------------
    pids["bitcoind"] = bitcoind.proc.pid
    PIDS_FILE.write_text(json.dumps(pids, indent=2))
    logger.info(f"PIDs written to {PIDS_FILE}")

    # ------------------------------------------------------------------
    # 9. Start RPC server and block until shutdown
    # ------------------------------------------------------------------
    server = HTTPServer(("127.0.0.1", RPC_PORT), RPCHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"RPC server listening on http://127.0.0.1:{RPC_PORT}")
    logger.info("Setup complete. Waiting for shutdown signal...")

    _shutdown_event.wait()
    logger.info("Shutting down RPC server.")
    server.shutdown()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--teardown", action="store_true")
    args = parser.parse_args()

    if args.teardown:
        teardown()
    else:
        setup()
