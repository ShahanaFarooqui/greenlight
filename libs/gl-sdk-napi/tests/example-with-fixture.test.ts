import { withGltestServer } from './fixtures';
import { Scheduler, Signer, Node } from '../index.js';

const MNEMONIC = 'spirit couple over surprise toilet dynamic maximum attitude scrap blush outdoor science';

describe('API tests', () => {
  it('should get data from server', async () => {
    await withGltestServer(async ({ metadata }) => {
      try {
        console.log('🚀 Creating scheduler...');
        const scheduler = new Scheduler('regtest');
        
        console.log('🚀 Creating signer...');
        const signer = new Signer(MNEMONIC);
        
        console.log('🚀 Recovering credentials...');
        const credentials = await scheduler.register(signer);
        
        console.log('🚀 Creating node...');
        const node = new Node(credentials);
        
        console.log('🚀 Getting node info...');
        const data = await node.getInfo();
        
        console.log('✅ Success! Node info:', data);
        expect(data.alias).toBe('');
        
      } catch (error) {
        console.error('❌ Test failed with error:', error);
        
        // Log the full error details
        if (error instanceof Error) {
          console.error('  Error name:', error.name);
          console.error('  Error message:', error.message);
          console.error('  Error stack:', error.stack);
        }
        
        // Re-throw to make the test fail
        throw error;
      }
    });
  });
});