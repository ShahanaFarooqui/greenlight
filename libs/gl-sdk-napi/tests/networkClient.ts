/**
 * networkClient.ts
 * ----------------
 * Typed helper for Jest tests to call the Python RPC server started by
 * setup_network.py. Import this in any test file instead of hardcoding
 * fetch() calls.
 *
 * Usage
 * -----
 *   import { network, NetworkConfig } from './networkClient';
 *
 *   let config: NetworkConfig;
 *   beforeAll(async () => { config = network.loadConfig(); });
 *
 *   it('creates a node', async () => {
 *     const node = await network.getNode();
 *     console.log(node.id, node.p2p_addr);
 *   });
 *
 *   it('creates and registers a GL client', async () => {
 *     const client = await network.newClient({ name: 'alice', register: true });
 *     const glNode = await network.getGlNode({ name: 'alice' });
 *   });
 */

import * as fs from 'fs';

const CONFIG_PATH = process.env.JEST_NETWORK_CONFIG ?? '/tmp/jest-gl-network.json';

// ---------------------------------------------------------------------------
// Types matching Python RPC responses
// ---------------------------------------------------------------------------
export interface NetworkConfig {
  rpc_url:            string;
  scheduler_grpc_uri: string;
  ca_crt_path:        string;
  nobody_crt_path:    string;
  nobody_key_path:    string;
  cert_path:          string;
  bitcoind_rpc_uri:   string;
  bitcoind_rpc_port:  number;
}

export interface NodeInfo {
  id:       string;
  rpc_path: string;
  p2p_addr: string;
}

export interface GlClientInfo {
  name:      string;
  id:        string;
  cert_path: string;
}

// ---------------------------------------------------------------------------
// RPC param shapes
// ---------------------------------------------------------------------------
export interface GetNodeParams {
  options?: Record<string, string | null>;
}

export interface NewClientParams {
  name?:      string;
  register?:  boolean;
  configure?: boolean;
}

export interface RegisterClientParams {
  name:       string;
  configure?: boolean;
}

export interface GetGlNodeParams {
  name:          string;
  start_signer?: boolean;
}

export interface ConnectPeerParams {
  name:      string;  // GL client name
  peer_id:   string;
  peer_addr: string;
}

export interface FundWalletParams {
  name: string;       // GL client name
  sats?: number;
}

export interface GenerateBlockParams {
  numblocks?:        number;
  wait_for_mempool?: number;
}

// ---------------------------------------------------------------------------
// Client implementation
// ---------------------------------------------------------------------------
class NetworkClient {
  private rpcUrl: string | null = null;

  /** Load the JSON config written by setup_network.py. Call in beforeAll(). */
  loadConfig(): NetworkConfig {
    if (!fs.existsSync(CONFIG_PATH)) {
      throw new Error(`Network config not found at ${CONFIG_PATH}. Is setup_network.py running?`);
    }
    const config: NetworkConfig = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    this.rpcUrl = config.rpc_url;
    return config;
  }

  private async call<T>(method: string, params: object = {}): Promise<T> {
    if (!this.rpcUrl) {
      // Auto-load if not done yet
      this.loadConfig();
    }
    const res = await fetch(this.rpcUrl!, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ method, params }),
    });
    const body = await res.json() as { result?: T; error?: string };
    if (body.error) throw new Error(`RPC error [${method}]: ${body.error}`);
    return body.result as T;
  }

  // -------------------------------------------------------------------------
  // Node factory methods
  // -------------------------------------------------------------------------

  /** Create a new CLN node via nf.get_node(). */
  getNode(params: GetNodeParams = {}): Promise<NodeInfo> {
    return this.call<NodeInfo>('get_node', params);
  }

  // -------------------------------------------------------------------------
  // GL client methods
  // -------------------------------------------------------------------------

  /** Create a new GL client, optionally registering it immediately. */
  newClient(params: NewClientParams = {}): Promise<GlClientInfo> {
    return this.call<GlClientInfo>('new_client', params);
  }

  /** Register an already-created GL client by name. */
  registerClient(params: RegisterClientParams): Promise<GlClientInfo> {
    return this.call<GlClientInfo>('register_client', params);
  }

  /**
   * Call c.node() on a GL client and optionally start its signer thread.
   * Must call newClient() (with register=true) first.
   */
  getGlNode(params: GetGlNodeParams): Promise<GlClientInfo> {
    return this.call<GlClientInfo>('get_gl_node', params);
  }

  // -------------------------------------------------------------------------
  // Network helpers
  // -------------------------------------------------------------------------

  /** Connect a GL node to a peer. */
  connectPeer(params: ConnectPeerParams): Promise<{ ok: boolean }> {
    return this.call<{ ok: boolean }>('connect_peer', params);
  }

  /** Send on-chain funds to a GL node and wait for confirmation. */
  fundWallet(params: FundWalletParams): Promise<{ address: string; sats: number }> {
    return this.call<{ address: string; sats: number }>('fund_wallet', params);
  }

  /** Mine blocks on bitcoind. */
  generateBlock(params: GenerateBlockParams = {}): Promise<{ blocks: number }> {
    return this.call<{ blocks: number }>('generate_block', params);
  }

  /** Call gl1.list_datastore(key=[...]) on a stored GL node handle. */
  listDatastore(params: ListDatastoreParams): Promise<ListDatastoreResult> {
    return this.call<ListDatastoreResult>('list_datastore', params);
  }

  /** Send shutdown signal to the Python server (called by globalTeardown). */
  shutdown(): Promise<{ ok: boolean }> {
    return this.call<{ ok: boolean }>('shutdown');
  }
}

// Singleton — import `network` in your tests, call loadConfig() in beforeAll()
export const network = new NetworkClient();

// Appended: listDatastore support
export interface ListDatastoreParams {
  name: string;   // GL client name
  key:  string[];
}

export interface DatastoreEntry {
  key:        string[];
  string?:    string;
  hex?:       string;
  generation: number;
}

export interface ListDatastoreResult {
  datastore: DatastoreEntry[];
}
