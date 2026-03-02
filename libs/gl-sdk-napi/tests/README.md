# GL SDK NAPI – Integration Test Setup

## Overview

```
make gltestserver            ← Terminal 1: long-running infrastructure
npm test                     ← Terminal 2: Jest test suite
```

---

## File layout

```
libs/
├── gl-sdk-napi/
│   ├── jest.config.js            ← updated (adds globalSetup, longer timeout)
│   ├── jest.globalSetup.ts       ← reads /tmp/gltestserver.env → injects env vars
│   └── __tests__/
│       └── integration/
│           └── payment.test.ts   ← main integration test
│
└── gl-testing/
    ├── gltestserver.py           ← `make gltestserver` target runs this
    └── node_factory_helper.py    ← called by payment.test.ts via child_process
```

Add these lines to the **existing** `Makefile` in `libs/gl-sdk-napi/`:

```makefile
.PHONY: gltestserver
gltestserver:
    python3 -m gltestserver --env-file /tmp/gltestserver.env
```

---

## Prerequisites

### Python packages
```bash
pip install mnemonic ephemeral-port-reserve
# gltesting and pyln-testing must already be on your PYTHONPATH
```

### Node packages (in libs/gl-sdk-napi)
```bash
npm install --save-dev ts-jest @types/jest jest jest-runner
```

### Build the NAPI module
```bash
cd libs/gl-sdk-napi
npm run build        # produces index.js + index.d.ts
```

---

## Running the tests

### Step 1 – Start the test server (Terminal 1)
```bash
cd libs/gl-sdk-napi
make gltestserver
```

The server prints `Server ready – press Ctrl-C to stop.` and writes:

| File | Contents |
|------|----------|
| `/tmp/gltestserver.env` | JSON with GL_CA_CRT, GL_NOBODY_CRT, GL_NOBODY_KEY, GL_SCHEDULER_GRPC_URI, BITCOIND_RPC_URL |

### Step 2 – Run tests (Terminal 2)
```bash
cd libs/gl-sdk-napi
npm test
# or with verbose output:
npx jest --verbose
```

`jest.globalSetup.ts` reads `/tmp/gltestserver.env` and injects the env vars
before any test file is loaded.

---

## Environment variables set by globalSetup

| Variable | Description |
|----------|-------------|
| `GL_CA_CRT` | Path to CA certificate PEM |
| `GL_NOBODY_CRT` | Path to nobody device certificate chain |
| `GL_NOBODY_KEY` | Path to nobody device private key |
| `GL_SCHEDULER_GRPC_URI` | gRPC URI of the test scheduler |
| `BITCOIND_RPC_URL` | Full RPC URL of the test bitcoind |
| `GL_TESTING_BASE_DIR` | Base temp directory for all test artefacts |

---

## What the integration test does

1. **Reads env vars** injected by `jest.globalSetup.ts`.
2. **Starts `node_factory_helper.py`** as a subprocess which provisions:
   - 2 plain CLN nodes (regtest)
   - 1 LSP node (CLN + LSPS2 plugin)
3. **Registers 2 Greenlight nodes** via `Scheduler.register()`.
4. **Runs payment scenarios:**
   - GL-A → LSP  (GL node pays CLN/LSP invoice)
   - LSP → GL-A  (CLN/LSP pays GL node invoice with JIT channel)
   - GL-A → GL-B  (GL-to-GL payment)
   - CLN-0 → GL-B (plain CLN pays GL node via LSP routing)
5. **Smoke-tests** `stream_node_events`, `list_funds`, and `onchain_receive`.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Missing GL_CA_CRT` | Start `make gltestserver` first |
| `lightning-cli: command not found` | Ensure CLN binaries are on `$PATH` (the `paths` fixture in fixtures.py handles this for pytest; for Jest you may need to add the CLN bin dir to `$PATH` manually) |
| Channel tests time out | Mine more blocks: `lightning-cli --rpc-file=<socket> dev-mine 6` |
| `Unimplemented` from `stream_node_events` | The connected GL build doesn't support `StreamNodeEvents` yet – the test warns and continues |
