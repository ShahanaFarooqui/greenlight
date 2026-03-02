import fs from 'fs/promises';
import path from 'path';
import { randomUUID } from 'crypto';
import { execa } from '@esm2cjs/execa';

export interface GltestServerContext {
  metadata: {
    scheduler_grpc_uri: string;
    grpc_web_proxy_uri: string;
    bitcoind_rpc_uri: string;
    cert_path: string;
    ca_crt_path: string;
    nobody_crt_path: string;
    nobody_key_path: string;
    [key: string]: any; // For any additional fields
  };
  directory: string;
}

export async function withGltestServer(testFn: (context: GltestServerContext) => Promise<void>) {
  const testId = randomUUID();
  const testDir = `/tmp/gltests/${testId}`;
  await fs.mkdir(testDir, { recursive: true });
  
  let serverProcess;
  const originalEnv = { ...process.env };
  const setEnvVars: string[] = [];
  
  try {
    // Start server
    serverProcess = execa('uv', ['run', 'gltestserver', 'run', '--directory', testDir], {
      detached: true,
      stdio: 'pipe',
    });
    
    // Wait for metadata.json
    const metadataPath = path.join(testDir, 'metadata.json');
    await waitForFile(metadataPath);
    const metadataContent = await fs.readFile(metadataPath, 'utf-8');
    const metadata = JSON.parse(metadataContent);
    
    console.log('📋 Metadata from server:', metadata);
    console.log('📍 Scheduler URI from metadata:', metadata.scheduler_grpc_uri);
    
    // Set environment variables from metadata
    process.env.GL_SCHEDULER_GRPC_URI = metadata.scheduler_grpc_uri;
    process.env.GL_CERT_PATH = metadata.cert_path;
    process.env.GL_CA_CRT = metadata.ca_crt_path;
    process.env.GL_NOBODY_CRT = metadata.nobody_crt_path;
    process.env.GL_NOBODY_KEY = metadata.nobody_key_path;
    
    // Track which vars we set
    setEnvVars.push(
      'GL_SCHEDULER_GRPC_URI',
      'GL_CERT_PATH', 
      'GL_CA_CRT',
      'GL_NOBODY_CRT',
      'GL_NOBODY_KEY'
    );
    
    console.log('🔧 Environment variables set:');
    console.log('  GL_SCHEDULER_GRPC_URI:', process.env.GL_SCHEDULER_GRPC_URI);
    console.log('  GL_CA_CRT:', process.env.GL_CA_CRT);
    console.log('  GL_NOBODY_CRT:', process.env.GL_NOBODY_CRT);
    console.log('  GL_NOBODY_KEY:', process.env.GL_NOBODY_KEY);
    
    // Check if .env file exists and parse it
    const envPath = path.join(testDir, '.env');
    try {
      const envContent = await fs.readFile(envPath, 'utf-8');
      console.log('📄 .env file contents:', envContent);
      
      const envVars = parseEnvFile(envContent);
      
      // Set any additional env vars from .env
      Object.entries(envVars).forEach(([key, value]) => {
        if (!process.env[key]) { // Don't overwrite if already set
          process.env[key] = value;
          setEnvVars.push(key);
          console.log(`  ${key}: ${value} (from .env)`);
        }
      });
    } catch (error) {
      console.log('No .env file found or error reading it');
    }
    
    await testFn({
      metadata,
      directory: testDir,
    });
    
  } finally {
    // Restore original environment
    console.log('🧹 Cleaning up - restoring original environment');
    setEnvVars.forEach(key => {
      if (originalEnv[key] !== undefined) {
        process.env[key] = originalEnv[key];
      } else {
        delete process.env[key];
      }
    });
    
    // Cleanup server
    if (serverProcess?.pid) {
      try {
        process.kill(-serverProcess.pid);
        console.log('✅ Server process killed');
      } catch (error) {
        console.error('Failed to kill server process:', error);
      }
    }
    
    // Cleanup directory
    try {
      await fs.rm(testDir, { recursive: true, force: true });
      console.log('✅ Test directory cleaned up');
    } catch (error) {
      console.error('Failed to clean up test directory:', error);
    }
  }
}

function parseEnvFile(content: string): Record<string, string> {
  const env: Record<string, string> = {};
  
  content.split('\n').forEach(line => {
    const match = line.match(/^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$/);
    if (match) {
      const [, key, value] = match;
      // Remove quotes if present
      env[key] = value.replace(/^["']|["']$/g, '');
    }
  });
  
  return env;
}

function waitForFile(filePath: string, timeout = 5000): Promise<void> {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const check = async () => {
      try {
        await fs.access(filePath);
        resolve();
      } catch {
        if (Date.now() - start > timeout) {
          reject(new Error(`Timeout waiting for ${filePath}`));
        } else {
          setTimeout(check, 100);
        }
      }
    };
    check();
  });
}
