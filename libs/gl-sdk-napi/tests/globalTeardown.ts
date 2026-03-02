/**
 * globalTeardown.ts
 * -----------------
 * Sends /shutdown to the Python RPC server. Falls back to SIGTERM if the
 * HTTP call fails (e.g. server already dead).
 */

import * as fs from 'fs';

const CONFIG_PATH = process.env.JEST_NETWORK_CONFIG ?? '/tmp/jest-gl-network.json';
const PIDS_PATH   = '/tmp/jest-gl-network.pids';

export default async function globalTeardown(): Promise<void> {
  console.log('[globalTeardown] Shutting down network...');

  // Try graceful RPC shutdown first
  if (fs.existsSync(CONFIG_PATH)) {
    try {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
      await fetch(`${config.rpc_url}`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ method: 'shutdown', params: {} }),
      });
      console.log('[globalTeardown] Shutdown RPC sent.');
      // Give the server a moment to stop
      await new Promise(r => setTimeout(r, 2000));
    } catch (e) {
      console.warn('[globalTeardown] RPC shutdown failed, falling back to SIGTERM:', e);
    }
  }

  // Fallback: kill via saved PID
  if (fs.existsSync(PIDS_PATH)) {
    const pids = JSON.parse(fs.readFileSync(PIDS_PATH, 'utf-8'));
    for (const [name, pid] of Object.entries(pids)) {
      try {
        process.kill(pid as number, 'SIGTERM');
        console.log(`[globalTeardown] Killed ${name} (pid=${pid})`);
      } catch {
        // already gone
      }
    }
    fs.unlinkSync(PIDS_PATH);
  }

  if (fs.existsSync(CONFIG_PATH)) fs.unlinkSync(CONFIG_PATH);
  console.log('[globalTeardown] Done.');
}
