#!/usr/bin/env python3
"""
node_factory_helper.py
======================
Called by Jest tests (via `spawnSync`) to provision CLN nodes and the LSPS
server through the same fixtures used in gltesting.

Usage
-----
  python3 node_factory_helper.py provision --nodes 2 --lsp 1 --out /tmp/nodes.json

The script reads the GL env vars already present in the environment (injected
by jest.globalSetup.ts), spins up the requested nodes, and writes a JSON file
containing the nodes' RPC socket paths, ports, and node-ids so the Jest tests
can call into them.

The process keeps running (blocking on stdin) until the parent sends EOF /
SIGTERM, at which point everything is torn down.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                    format="[node_factory_helper] %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def _bitcoind_from_env():
    """Re-use the bitcoind that gltestserver already started."""
    from pyln.testing.utils import BitcoinD
    # We don't start a *new* bitcoind; we connect to the one whose RPC URL was
    # exported by gltestserver via BITCOIND_RPC_URL.
    rpc_url = os.environ.get("BITCOIND_RPC_URL", "")
    if not rpc_url:
        raise RuntimeError("BITCOIND_RPC_URL not set; is gltestserver running?")

    # Parse http://user:password@host:port
    import urllib.parse as up
    parsed = up.urlparse(rpc_url)
    from pyln.testing.utils import SimpleBitcoinProxy
    proxy = SimpleBitcoinProxy(
        btc_conf_file=None,
        btcconn=rpc_url,
    )
    return proxy


def provision(args):
    base_dir = Path(os.environ.get("GL_TESTING_BASE_DIR", "/tmp/gltestserver"))
    nodes_dir = base_dir / "cln_nodes"
    nodes_dir.mkdir(parents=True, exist_ok=True)

    from pyln.testing.utils import NodeFactory, BitcoinD
    import bitcoin.rpc as _unused  # ensure pyln extras present

    # We need a real BitcoinD object (not just a proxy) for NodeFactory.
    bitcoind_dir = base_dir / "bitcoind"
    bd = BitcoinD(bitcoin_dir=str(bitcoind_dir))
    # Don't re-start; just attach to the running instance.
    bd.start()  # idempotent if already started

    node_factory = NodeFactory(
        testname="jest_integration",
        executor=None,           # pyln accepts None here for sync usage
        bitcoind=bd,
        directory=str(nodes_dir),
    )

    output: dict = {"cln_nodes": [], "lsp_node": None}

    # ── plain CLN nodes ──────────────────────────────────────────────────────
    if args.nodes > 0:
        cln_nodes = node_factory.get_nodes(args.nodes)
        for n in cln_nodes:
            output["cln_nodes"].append({
                "node_id": n.info["id"],
                "rpc_file": n.rpc.socket_path,
                "port":     n.daemon.port,
                "grpc_port": getattr(n, "grpc_port", None),
            })
        log.info("Provisioned %d CLN nodes.", args.nodes)

    # ── LSP node ─────────────────────────────────────────────────────────────
    if args.lsp:
        from gltesting import get_plugins_dir
        policy_plugin = get_plugins_dir() / "lsps2_policy.py"

        lsp = node_factory.get_node(
            options={
                "experimental-lsps2-service": None,
                "experimental-lsps2-promise-secret": "A" * 64,
                "important-plugin": str(policy_plugin),
                "disable-plugin": "cln-grpc",
            }
        )
        output["lsp_node"] = {
            "node_id": lsp.info["id"],
            "rpc_file": lsp.rpc.socket_path,
            "port":     lsp.daemon.port,
        }
        log.info("Provisioned LSP node.")

    # ── write output JSON ─────────────────────────────────────────────────────
    out_path = Path(args.out)
    out_path.write_text(json.dumps(output, indent=2))
    log.info("Node info written to %s", out_path)

    # Signal readiness to the parent process on stdout
    print("READY", flush=True)

    # Block until EOF on stdin (parent closes pipe) or SIGTERM
    stop = {"flag": False}
    def _stop(sig, frame):
        stop["flag"] = True
    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT,  _stop)

    try:
        while not stop["flag"]:
            line = sys.stdin.readline()
            if line == "":   # EOF
                break
            time.sleep(0.1)
    finally:
        log.info("Tearing down CLN nodes…")
        node_factory.killall(["lightningd"])
        log.info("Done.")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    p_prov = sub.add_parser("provision")
    p_prov.add_argument("--nodes", type=int, default=2)
    p_prov.add_argument("--lsp",   action="store_true")
    p_prov.add_argument("--out",   required=True)

    args = parser.parse_args()

    if args.command == "provision":
        provision(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
