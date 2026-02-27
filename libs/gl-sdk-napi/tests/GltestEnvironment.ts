/**
 * GltestEnvironment.ts
 *
 * Custom Jest test environment. Jest creates a fresh instance of this class
 * for every test FILE, calling setup() before any tests run and teardown()
 * after. Because setup() runs before any module code executes, env vars set
 * here via process.env are visible to native addons (Rust/NAPI) that read
 * the real OS environment at load time.
 *
 * Register in jest.config.ts:
 *   testEnvironment: '<rootDir>/tests/GltestEnvironment.ts'
 */

import { TestEnvironment } from 'jest-environment-node';
import type { EnvironmentContext, JestEnvironmentConfig } from '@jest/environment';
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
  // Wait for ca.crt to be fully written before returning
  await pollForFile(metadata.ca_crt_path, timeoutMs);
  return metadata;
}

export default class GltestEnvironment extends TestEnvironment {
  private child: ChildProcess | null = null;
  private testDir: string | null = null;

  constructor(config: JestEnvironmentConfig, context: EnvironmentContext) {
    super(config, context);
  }

  async setup(): Promise<void> {
    await super.setup();

    this.testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'gl-test-'));
    const metadataPath = path.join(this.testDir, 'metadata.json');

    this.child = spawn(
      'uv',
      ['run', 'gltestserver', 'run', `--directory=${this.testDir}`],
      {
        // Inherit the current process env so uv/python can find dependencies
        env: { ...process.env },
        stdio: ['ignore', 'pipe', 'pipe'],
        detached: false,
      }
    );

    this.child.stdout?.on('data', (d: Buffer) => process.stdout.write(`[gltestserver] ${d}`));
    this.child.stderr?.on('data', (d: Buffer) => process.stderr.write(`[gltestserver] ${d}`));
    this.child.on('error', (err) => { throw new Error(`Failed to spawn gltestserver: ${err.message}`); });

    const metadata = await pollForMetadata(metadataPath, READY_TIMEOUT_MS);

    // Set on the real process.env — native addons see these immediately because
    // setup() runs before any test module is required/loaded.
    process.env.GL_SCHEDULER_GRPC_URI = metadata.scheduler_grpc_uri;
    process.env.GL_CA_CRT             = metadata.ca_crt_path;
    process.env.GL_NOBODY_CRT         = metadata.nobody_crt_path;
    process.env.GL_NOBODY_KEY         = metadata.nobody_key_path;
    process.env.GL_BITCOIND_RPC_URI   = metadata.bitcoind_rpc_uri;
    process.env.GL_GRPC_WEB_PROXY_URI = metadata.grpc_web_proxy_uri;
    process.env.GL_CERT_PATH          = metadata.cert_path;

    // Also expose on the sandbox global so test code can read them
    this.global.process.env.GL_SCHEDULER_GRPC_URI = metadata.scheduler_grpc_uri;
    this.global.process.env.GL_CA_CRT             = metadata.ca_crt_path;
    this.global.process.env.GL_NOBODY_CRT         = metadata.nobody_crt_path;
    this.global.process.env.GL_NOBODY_KEY         = metadata.nobody_key_path;
    this.global.process.env.GL_BITCOIND_RPC_URI   = metadata.bitcoind_rpc_uri;
    this.global.process.env.GL_GRPC_WEB_PROXY_URI = metadata.grpc_web_proxy_uri;
    this.global.process.env.GL_CERT_PATH          = metadata.cert_path;
  }

  async teardown(): Promise<void> {
    if (this.child) {
      this.child.kill('SIGTERM');
      await new Promise<void>((resolve) => {
        const t = setTimeout(() => { this.child?.kill('SIGKILL'); resolve(); }, 5_000);
        this.child!.once('exit', () => { clearTimeout(t); resolve(); });
      });
      this.child = null;
    }

    if (this.testDir && fs.existsSync(this.testDir)) {
      fs.rmSync(this.testDir, { recursive: true, force: true });
      this.testDir = null;
    }

    await super.teardown();
  }
}
