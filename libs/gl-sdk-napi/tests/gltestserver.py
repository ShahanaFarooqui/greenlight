#!/usr/bin/env python3
"""
gltestserver.py  –  Long-running process that boots the GL test infrastructure
(bitcoind + scheduler + certs) and exposes the resulting environment variables
so that Jest globalSetup can pick them up.

Usage (matches `make gltestserver`):
    python3 -m gltestserver --env-file /tmp/gltestserver.env

The process blocks until it receives SIGINT / SIGTERM, then tears everything
down cleanly.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import tempfile
import time
from decimal import Decimal
from pathlib import Path

from ephemeral_port_reserve import reserve

# ── gltesting imports ────────────────────────────────────────────────────────
from gltesting import certs
from gltesting.scheduler import Scheduler

# pyln bitcoind fixture (we instantiate it manually here)
from pyln.testing.utils import BitcoinD

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format="[gltestserver] %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── helpers ──────────────────────────────────────────────────────────────────

def _make_bitcoind(directory: Path) -> BitcoinD:
    btc_dir = directory / "bitcoind"
    btc_dir.mkdir(parents=True, exist_ok=True)
    bd = BitcoinD(bitcoin_dir=str(btc_dir))
    bd.start()
    bd.generate_block(101)          # enough coins + past coinbase maturity
    return bd


def _mock_feerates(btcproxy):
    feerates = (15000, 11000, 7500, 3750)

    def mock_estimatesmartfee(r):
        params = r["params"]
        mapping = {
            (2, "CONSERVATIVE"): feerates[0],
            (6, "ECONOMICAL"):   feerates[1],
            (12, "ECONOMICAL"):  feerates[2],
            (100, "ECONOMICAL"): feerates[3],
        }
        feerate = mapping.get(tuple(params), 42)
        return {
            "id": r["id"],
            "error": None,
            "result": {"feerate": Decimal(feerate * 4) / 10**8},
        }

    btcproxy.mock_rpc("estimatesmartfee", mock_estimatesmartfee)


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", required=True,
                        help="Path where env-vars JSON is written for Jest")
    args = parser.parse_args()

    env_path = Path(args.env_file)

    # Use a stable temp directory so paths survive across the process lifetime
    base_dir = Path(tempfile.mkdtemp(prefix="gltestserver_"))
    cert_dir = base_dir / "certs"
    cert_dir.mkdir(parents=True, exist_ok=True)

    log.info("Working directory: %s", base_dir)

    # ── certs ────────────────────────────────────────────────────────────────
    os.environ["GL_CERT_PATH"] = str(cert_dir)
    os.environ["GL_CA_CRT"]    = str(cert_dir / "ca.pem")

    root_id      = certs.genca("/")
    _            = certs.genca("/services")
    scheduler_id = certs.gencert("/services/scheduler")
    _            = certs.genca("/users")
    nobody_id    = certs.gencert("/users/nobody")

    os.environ["GL_NOBODY_CRT"] = str(nobody_id.cert_chain_path)
    os.environ["GL_NOBODY_KEY"] = str(nobody_id.private_key_path)

    log.info("Certificates generated.")

    # ── bitcoind ─────────────────────────────────────────────────────────────
    bitcoind = _make_bitcoind(base_dir)
    btcproxy = bitcoind.get_proxy()
    _mock_feerates(btcproxy)
    log.info("bitcoind started.")

    # ── scheduler ────────────────────────────────────────────────────────────
    grpc_port = reserve()
    scheduler = Scheduler(
        bitcoind=btcproxy,
        grpc_port=grpc_port,
        identity=scheduler_id,
    )
    scheduler.start()
    os.environ["GL_SCHEDULER_GRPC_URI"] = scheduler.grpc_addr
    log.info("Scheduler started at %s", scheduler.grpc_addr)

    # ── write env file ───────────────────────────────────────────────────────
    env_vars = {
        "GL_CERT_PATH":           str(cert_dir),
        "GL_CA_CRT":              str(cert_dir / "ca.pem"),
        "GL_NOBODY_CRT":          str(nobody_id.cert_chain_path),
        "GL_NOBODY_KEY":          str(nobody_id.private_key_path),
        "GL_SCHEDULER_GRPC_URI":  scheduler.grpc_addr,
        # Pass bitcoind RPC details so node_factory can connect
        "BITCOIND_RPC_URL":       f"http://{bitcoind.rpcuser}:{bitcoind.rpcpassword}@127.0.0.1:{bitcoind.rpcport}",
        "GL_TESTING_BASE_DIR":    str(base_dir),
    }

    env_path.write_text(json.dumps(env_vars, indent=2))
    log.info("Env-file written to %s", env_path)
    log.info("Server ready – press Ctrl-C to stop.")

    # ── block until signal ───────────────────────────────────────────────────
    stop = {"flag": False}

    def _stop(sig, frame):
        log.info("Received signal %s, shutting down…", sig)
        stop["flag"] = True

    signal.signal(signal.SIGINT,  _stop)
    signal.signal(signal.SIGTERM, _stop)

    while not stop["flag"]:
        time.sleep(0.5)

    # ── teardown ─────────────────────────────────────────────────────────────
    log.info("Stopping scheduler…")
    scheduler.stop()

    log.info("Stopping bitcoind…")
    bitcoind.stop()

    env_path.unlink(missing_ok=True)
    log.info("Done.")


if __name__ == "__main__":
    main()
