import { Scheduler, Signer, Node } from '../index.js';

describe('test basic connection', () => {
  it('different node ids', async () => {
    const scheduler = new Scheduler('regtest');
    const signer1 = new Signer('spirit couple over surprise toilet dynamic maximum attitude scrap blush outdoor science');
    const signer2 = new Signer('abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about');
    const credentials1 = await scheduler.register(signer1);
    const credentials2 = await scheduler.register(signer2);
    const node1 = new Node(credentials1);
    const node2 = new Node(credentials2);
    const initialInfo1 = await node1.getInfo();
    const initialInfo2 = await node2.getInfo();
    console.log('Initial Info 1:', initialInfo1);
    console.log('Initial Info 2:', initialInfo2);
    expect(initialInfo1.alias).toEqual('VIOLETWATCH-v25.12gl1');
    expect(initialInfo2.alias).toEqual('PEEVEDGENESIS-v25.12gl1');
  });

  it('connects two gl nodes', async () => {
    const scheduler = new Scheduler('regtest');
    const signer1 = new Signer('spirit couple over surprise toilet dynamic maximum attitude scrap blush outdoor science');
    const credentials1 = await scheduler.register(signer1);
    const node1 = new Node(credentials1);
    const initialInfo1 = await node1.onchainReceive();
    console.log('Initial Info 1:', initialInfo1);
    expect(initialInfo1).toEqual('PEEVEDGENESIS-v25.12gl1');
  });
});
