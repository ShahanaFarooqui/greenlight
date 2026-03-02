/**
 * example.test.ts
 * ---------------
 * Mirrors the Python test pattern:
 *
 *   l1 = node_factory.get_node()
 *   c  = clients.new()
 *   c.register()
 *   gl1 = c.node()
 *   s   = c.signer().run_in_thread()
 *   gl1.connect_peer(l1.info['id'], f'127.0.0.1:{l1.daemon.port}')
 *   res = gl1.list_datastore(key=["greenlight", "peerlist"])
 */

import { network, NetworkConfig, NodeInfo, GlClientInfo } from './networkClient';

let config: NetworkConfig;

beforeAll(() => {
  config = network.loadConfig();
});

describe('test_peerlist_datastore_add', () => {
  it('connects a GL node to a peer and checks the peerlist datastore', async () => {
    // l1 = node_factory.get_node()
    const l1: NodeInfo = await network.getNode();

    // c = clients.new() + c.register()
    const client: GlClientInfo = await network.newClient({
      name:     'alice',
      register: true,
    });

    // gl1 = c.node()  +  s = c.signer().run_in_thread()
    await network.getGlNode({ name: 'alice', start_signer: true });

    // gl1.connect_peer(l1.info['id'], f'127.0.0.1:{l1.daemon.port}')
    await network.connectPeer({
      name:      'alice',
      peer_id:   l1.id,
      peer_addr: l1.p2p_addr,
    });

    // res = gl1.list_datastore(key=["greenlight", "peerlist"])
    // assert l1.info['id'] in res.datastore[0].key
    const res = await network.listDatastore({
      name: 'alice',
      key:  ['greenlight', 'peerlist'],
    });
    expect(res.datastore.length).toBeGreaterThan(0);
    expect(res.datastore[0].key).toContain(l1.id);
  });
});
