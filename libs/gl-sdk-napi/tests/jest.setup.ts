/**
 * jest.setup.ts
 *
 * beforeEach/afterEach hooks that give every it() a fresh gltestserver.
 * By this point the native addon is already loaded (GltestEnvironment.setup()
 * ran first), so updating process.env here is sufficient — the Rust code
 * calls getenv() on each SDK call, not at module load time.
 */

import { spawn, ChildProcess } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

const POLL_INTERVAL_MS = 500;
const READY_TIMEOUT_MS = 120_000;

interface ServerMetadata {
  scheduler_grpc_uri: string;
  grpc_web_proxy_uri: string;
  bitcoind_rpc_uri:   string;
  cert_path:          string;
  ca_crt_path:        string;
  nobody_crt_path:    string;
  nobody_key_path:    string;
}

function pollForFile(filePath: string, timeoutMs: number): Promise<string> {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeoutMs;
    const tick = () => {
      if (!fs.existsSync(filePath)) {
        if (Date.now() > deadline) return reject(new Error(`Timed out waiting for ${filePath}`));
        return setTimeout(tick, POLL_INTERVAL_MS);
      }
      try {
        const raw = fs.readFileSync(filePath, 'utf8').trim();
        if (!raw) {
          if (Date.now() > deadline) return reject(new Error(`${filePath} empty after timeout`));
          return setTimeout(tick, POLL_INTERVAL_MS);
        }
        resolve(raw);
      } catch {
        if (Date.now() > deadline) return reject(new Error(`Failed to read ${filePath} after timeout`));
        setTimeout(tick, POLL_INTERVAL_MS);
      }
    };
    tick();
  });
}

async function pollForMetadata(filePath: string, timeoutMs: number): Promise<ServerMetadata> {
  const raw = await pollForFile(filePath, timeoutMs);
  const metadata = JSON.parse(raw) as ServerMetadata;
  await pollForFile(metadata.ca_crt_path, timeoutMs);
  return metadata;
}

let currentServer: ChildProcess | null = null;
let currentTestDir: string | null = null;

beforeEach(async () => {
  currentTestDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gl-test-'));
  const metadataPath = path.join(currentTestDir, 'metadata.json');

  currentServer = spawn(
    'uv',
    ['run', 'gltestserver', 'run', `--directory=${currentTestDir}`],
    { env: { ...process.env }, stdio: ['ignore', 'pipe', 'pipe'], detached: false }
  );

  currentServer.stdout?.on('data', (d: Buffer) => process.stdout.write(`[gltestserver] ${d}`));
  currentServer.stderr?.on('data', (d: Buffer) => process.stderr.write(`[gltestserver] ${d}`));

  const metadata = await pollForMetadata(metadataPath, READY_TIMEOUT_MS);

  // Update process.env for this test — Rust reads getenv() on each call
  process.env.GL_SCHEDULER_GRPC_URI = metadata.scheduler_grpc_uri;
  process.env.GL_CA_CRT             = metadata.ca_crt_path;
  process.env.GL_NOBODY_CRT         = metadata.nobody_crt_path;
  process.env.GL_NOBODY_KEY         = metadata.nobody_key_path;
  process.env.GL_BITCOIND_RPC_URI   = metadata.bitcoind_rpc_uri;
  process.env.GL_GRPC_WEB_PROXY_URI = metadata.grpc_web_proxy_uri;
  process.env.GL_CERT_PATH          = metadata.cert_path;
});

afterEach(async () => {
  if (currentServer) {
    currentServer.kill('SIGTERM');
    await new Promise<void>((resolve) => {
      const t = setTimeout(() => { currentServer?.kill('SIGKILL'); resolve(); }, 5_000);
      currentServer!.once('exit', () => { clearTimeout(t); resolve(); });
    });
    currentServer = null;
  }

  if (currentTestDir && fs.existsSync(currentTestDir)) {
    fs.rmSync(currentTestDir, { recursive: true, force: true });
    currentTestDir = null;
  }
});
