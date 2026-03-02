/**
 * jest.globalSetup.ts
 *
 * Reads the env-file produced by `make gltestserver` (or gltestserver.py) and
 * injects every key into `process.env` so that all test workers see them.
 *
 * The env-file path defaults to /tmp/gltests/.env but can be overridden
 * via the GL_TESTSERVER_ENV_FILE environment variable.
 */

import fs from "fs";
import path from "path";

const ENV_FILE =
  process.env.GL_TESTSERVER_ENV_FILE ?? "/tmp/gltests/.env";

export default async function globalSetup(): Promise<void> {
  if (!fs.existsSync(ENV_FILE)) {
    throw new Error(
      `[jest.globalSetup] GL test-server env-file not found: ${ENV_FILE}\n` +
        "Run `make gltestserver` in a separate terminal before running the tests."
    );
  }

  const raw = fs.readFileSync(ENV_FILE, "utf-8");

  // Parse shell `export KEY=VALUE` format
  const envVars: Record<string, string> = {};
  for (const line of raw.split("\n")) {
    const match = line.match(/^\s*export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)\s*$/);
    if (match) {
      const [, key, value] = match;
      // Strip surrounding quotes if present (single or double)
      envVars[key] = value.replace(/^(['"])(.*)\1$/, "$2");
    }
  }

  const required = [
    "GL_CA_CRT",
    "GL_NOBODY_CRT",
    "GL_NOBODY_KEY",
    "GL_SCHEDULER_GRPC_URI",
  ];

  for (const key of required) {
    if (!envVars[key]) {
      throw new Error(
        `[jest.globalSetup] Required env var "${key}" is missing from ${ENV_FILE}`
      );
    }
  }

  for (const [key, value] of Object.entries(envVars)) {
    process.env[key] = value;
  }

  console.log(
    "[jest.globalSetup] GL test-server env vars loaded from",
    ENV_FILE
  );
}