"""
Example script tests glsdk library usage for:
- Registration/Recovery
- Node creation
- Receiving payments
- Sending payments
"""

import os
from typing import Optional
from glsdk import Network, Scheduler, Signer, Credentials, Node, Error, ReceiveResponse, SendResponse, OnchainReceiveResponse, OnchainSendResponse


class GreenlightApp:
    """
    An application demonstrating Greenlight node operations using 
    The pattern follows the glsdk structure:
    - Signer: Created from a BIP39 mnemonic phrase
    - Scheduler: Handles node registration and recovery
    - Credentials: Contains node authentication information
    - Node: Main interface for Lightning operations
    """
    
    def __init__(self, phrase: str, network: Network):
        """
        Initialize the Greenlight application with 
        
        Args:
            phrase: BIP39 mnemonic phrase for node identity
            network: Network (Network.BITCOIN or Network.REGTEST)
        """
        self.phrase: str = phrase
        self.network: Network = network
        self.credentials: Optional[Credentials] = None
        self.scheduler: Scheduler = Scheduler(network)
        self.node: Optional[Node] = None
        
        # Create signer from mnemonic phrase
        self.signer: Signer = Signer(phrase)
        node_id = self.signer.node_id()
        
        print(f"✓ Signer created for network: {network}")
        print(f"✓ Node ID: {node_id.hex()}")

    def register_or_recover(self):
        """
        Registers or recovers a node on Greenlight using 
        
        This method will:
        1. Try to register a new node
        2. If registration fails (node exists), recover instead
        3. Store the returned credentials for future operations
        
        The credentials contain the node_id and mTLS client certificate
        for authenticating against the node.
        """
        try:
            print("Attempting to register node...")
            self.credentials = self.scheduler.register(self.signer, code="")
            print("✓ Node registered successfully")
        except Error as e:
            print(f"Registration failed (node may already exist): {e}")
            print("Attempting to recover node...")
            try:
                self.credentials = self.scheduler.recover(self.signer)
                print("✓ Node recovered successfully")
            except Error as recover_error:
                print(f"✗ Recovery also failed: {recover_error}")
                raise
    
    def create_node(self) -> Node:
        """
        Create a Node instance using the credentials.
        
        The Node is the main entrypoint to interact with the Lightning node.
        
        Returns:
            Node instance for making Lightning operations
        """
        if self.credentials is None:
            raise ValueError("Must register/recover before creating node")
        
        print("Creating node instance...")
        self.node = Node(self.credentials)
        print("✓ Node created successfully")
        return self.node
    
    def receive(
        self,
        label: str,
        description: str,
        amount_msat: Optional[int] = None
    ) -> ReceiveResponse:
        """
        Create a Lightning invoice to receive a payment.
        
        This method generates a BOLT11 invoice that includes negotiation 
        of an LSPS2 / JIT channel, meaning that if there is no channel 
        sufficient to receive the requested funds, the node will negotiate 
        an opening.
        
        Args:
            label: Unique label for the invoice
            description: Invoice description
            amount_msat: Optional amount in millisatoshis (None for any amount)
        
        Returns:
            ReceiveResponse containing the BOLT11 invoice string
        """
        if self.node is None:
            self.create_node()
        
        print(f"Creating invoice: {amount_msat or 'any'} msat - '{description}'")
        
        invoice = self.node.receive(
            label=label,
            description=description,
            amount_msat=amount_msat
        )
        print(f"✓ Invoice created successfully")
        return invoice
    
    def send(
        self,
        invoice: str,
        amount_msat: Optional[int] = None
    ) -> SendResponse:
        """
        Pay a Lightning invoice.
        
        Args:
            invoice: BOLT11 invoice string to pay
            amount_msat: Optional amount in millisatoshis (for zero-amount invoices)
        
        Returns:
            SendResponse containing payment details
        """
        if self.node is None:
            self.create_node()
        
        print(f"Paying invoice: {invoice[:50]}...")
        
        payment = self.node.send(invoice=invoice, amount_msat=amount_msat)
        print(f"✓ Payment sent successfully")
        return payment
    
    def onchain_receive(self) -> OnchainReceiveResponse:
        """
        Get an on-chain address to receive Bitcoin.
        
        Returns:
            OnchainReceiveResponse containing the Bitcoin address
        """
        if self.node is None:
            self.create_node()
        
        print("Generating on-chain receive address...")
        
        response = self.node.onchain_receive()
        print(f"✓ On-chain address generated")
        return response
    
    def onchain_send(
        self,
        destination: str,
        amount_or_all: str
    ) -> OnchainSendResponse:
        """
        Send Bitcoin on-chain.
        
        Args:
            destination: Bitcoin address to send to
            amount_or_all: Amount in satoshis or "all" to send all funds
        
        Returns:
            OnchainSendResponse containing transaction details
        """
        if self.node is None:
            self.create_node()
        
        print(f"Sending on-chain: {amount_or_all} to {destination}")
        
        response = self.node.onchain_send(
            destination=destination,
            amount_or_all=amount_or_all
        )
        print(f"✓ On-chain transaction sent")
        return response
    
    def stop_node(self):
        """Stop the node if it is currently running."""
        if self.node is not None:
            print("Stopping node...")
            self.node.stop()
            print("✓ Node stopped")
    
    def save_credentials(self, filepath: str):
        """
        Save credentials to a file.
        
        Args:
            filepath: Path to save credentials
        """
        if self.credentials is None:
            raise ValueError("No credentials to save")
        
        try:
            creds_bytes = self.credentials.save()
            with open(filepath, 'wb') as f:
                f.write(creds_bytes)
            print(f"✓ Credentials saved to {filepath}")
        except Exception as e:
            print(f"✗ Failed to save credentials: {e}")
            raise
    
    def load_credentials(self, filepath: str) -> Credentials:
        """
        Load credentials from a file.
        
        Args:
            filepath: Path to load credentials from
        
        Returns:
            Loaded credentials
        """
        try:
            with open(filepath, 'rb') as f:
                creds_bytes = f.read()
            
            self.credentials = Credentials.load(creds_bytes)
            print(f"✓ Credentials loaded from {filepath}")
            return self.credentials
        except Exception as e:
            print(f"✗ Failed to load credentials: {e}")
            raise


def main():
    """Main demonstration function using """
    print("=" * 70)
    print("GLSDK Example: Register, Create Node, and Create Invoice")
    print("Inspired by glclient GetInfoApp pattern")
    print("=" * 70)
    print()
    
    # Configuration
    # NOTE: These should be persisted and loaded from disk in production
    # Default test mnemonic (DO NOT USE IN PRODUCTION)s
    phrase = ("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about")
    network = Network.REGTEST  # Options: BITCOIN, REGTEST
    
    # Step 1: Initialize applications
    print("Step 1: Initializing Applications")
    print("-" * 70)
    app = GreenlightApp(phrase, network)
    print()
    
    # Step 2: Register or recover nodes
    print("Step 2: Register or Recover Node")
    print("-" * 70)
    try:
        app.register_or_recover()
    except Exception as e:
        print(f"✗ Failed to register/recover: {e}")
        print("Note: This may fail without a proper Greenlight environment")
        import traceback
        traceback.print_exc()
        return
    print()
    
    # Step 3: Create the node
    print("Step 3: Creating Node")
    print("-" * 70)
    try:
        app.create_node()
    except Exception as e:
        print(f"✗ Failed to create node: {e}")
        import traceback
        traceback.print_exc()
        return
    print()
    
    # Step 4: Create an invoice (receive payment)
    print("Step 4: Creating Invoice (Receive)")
    print("-" * 70)
    try:
        invoice_response = app.receive(
            label=f"test-invoice-{os.urandom(4).hex()}",
            description="Test payment for GLSDK demo",
            amount_msat=100000,
        )
        print(f"Invoice response: {invoice_response}")
    except Exception as e:
        print(f"✗ Failed to create invoice: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Step 5: Generate on-chain receive address
    print("Step 5: On-chain Receive Address")
    print("-" * 70)
    try:
        onchain_response = app.onchain_receive()
        print(f"Onchain receive Bech32: {onchain_response.bech32()}, P2TR: {onchain_response.p2tr()}")
    except Exception as e:
        print(f"✗ Failed to get on-chain address: {e}")
        import traceback
        traceback.print_exc()
    print()
    
    # Step 6: Save credentials (optional)
    print("Step 6: Saving Credentials")
    print("-" * 70)
    try:
        if app.credentials:
            app.save_credentials("/tmp/glsdk_credentials.bin")
    except Exception as e:
        print(f"Note: Credential saving: {e}")
    print()
    
    # Step 7: Stop the node
    print("Step 7: Stopping Node")
    print("-" * 70)
    try:
        app.stop_node()
    except Exception as e:
        print(f"Note: Node stop: {e}")
    print()
    
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    """
    python glsdk_example.py
    """
    try:
        main()
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
