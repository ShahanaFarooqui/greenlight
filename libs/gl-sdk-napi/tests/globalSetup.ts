/**
 * globalSetup.ts
 * --------------
 * Spawns setup_network.py as a background process and waits until it has
 * written /tmp/jest-gl-network.json (the readiness signal).
 */

import { execSync, spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

const CONFIG_PATH  = process.env.JEST_NETWORK_CONFIG ?? '/tmp/jest-gl-network.json';
const PIDS_PATH    = '/tmp/jest-gl-network.pids';
const READY_TIMEOUT_MS = 120_000;  // 2 minutes
const POLL_INTERVAL_MS = 500;

const GREENLIGHT_ROOT = process.env.GREENLIGHT_ROOT
  ?? path.join(process.env.HOME!, 'workspace', 'greenlight');

const SETUP_SCRIPT = path.join(__dirname, 'setup_network.py');

const PYTHONPATH = [
  path.join(GREENLIGHT_ROOT, 'libs', 'gl-testing'),
  path.join(GREENLIGHT_ROOT, 'libs', 'gl-client-py'),
].join(':');

export default async function globalSetup(): Promise<void> {
  // Clean up any stale config from a previous run
  if (fs.existsSync(CONFIG_PATH)) fs.unlinkSync(CONFIG_PATH);

  console.log('[globalSetup] Starting setup_network.py...');

  // Spawn setup_network.py in the background — it blocks until shutdown
  const child = spawn('uv', ['run', 'python3', SETUP_SCRIPT], {
    env: {
      ...process.env,
      GREENLIGHT_ROOT,
      PYTHONPATH,
    },
    stdio: 'inherit',  // pipe output to Jest's stdout so we see logs
    detached: false,
  });

  child.on('error', (err) => {
    throw new Error(`[globalSetup] Failed to spawn setup_network.py: ${err.message}`);
  });

  // Save child PID so globalTeardown can kill it if /shutdown RPC fails
  fs.writeFileSync(PIDS_PATH, JSON.stringify({ setup_network: child.pid }, null, 2));

  // Poll for the readiness file
  console.log(`[globalSetup] Waiting for ${CONFIG_PATH} ...`);
  const deadline = Date.now() + READY_TIMEOUT_MS;

  await new Promise<void>((resolve, reject) => {
    const interval = setInterval(() => {
      if (fs.existsSync(CONFIG_PATH)) {
        clearInterval(interval);
        resolve();
      } else if (Date.now() > deadline) {
        clearInterval(interval);
        child.kill();
        reject(new Error(`[globalSetup] Timed out waiting for ${CONFIG_PATH}`));
      }
    }, POLL_INTERVAL_MS);
  });

  console.log('[globalSetup] Network is ready.');
}
