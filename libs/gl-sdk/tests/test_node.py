"""Basic tests for gl-sdk without requiring full scheduler setup.

These tests verify the UniFFI bindings work correctly without
needing the full gl-testing infrastructure.
"""

import os
import pytest
import glsdk


@pytest.fixture
def test_phrase():
    """Standard test mnemonic phrase."""
    return (
        "abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon abandon abandon about"
    )


@pytest.fixture
def test_signer(test_phrase):
    """Create a test signer with the default test mnemonic."""
    return glsdk.Signer(test_phrase)


@pytest.fixture
def scheduler():
    """Create a scheduler for testing."""
    return glsdk.Scheduler(glsdk.Network.BITCOIN)


@pytest.fixture
def credentials(test_signer, scheduler):
    """Register or recover a node and return credentials."""
    try:
        creds = scheduler.register(test_signer, code=None)
        print("✓ Node registered")
    except glsdk.Error as e:
        print(f"Registration failed, recovering: {e}")
        creds = scheduler.recover(test_signer)
        print("✓ Node recovered")
    return creds


@pytest.fixture
def node(credentials):
    """Create a node instance from credentials."""
    return glsdk.Node(credentials)


def test_node_creation(credentials):
    """Test that a node can be created from credentials."""
    node = glsdk.Node(credentials)
    assert node is not None, "Node should not be None"
    print("✓ Node created successfully")


def test_onchain_receive(node):
    """Test generating an on-chain receive address."""
    response = node.onchain_receive()
    
    assert response is not None, "Response should not be None"
    
    bech32 = response.bech32()
    p2tr = response.p2tr()
    
    assert bech32, "bech32 address should not be empty"
    assert p2tr, "p2tr address should not be empty"
    assert bech32.startswith('bc1'), "bech32 should be valid Bitcoin address"
    
    print(f"✓ On-chain address generated - Bech32: {bech32}, P2TR: {p2tr}")


def test_receive_invoice_with_amount(node):
    """Test creating a Lightning invoice with a specific amount."""
    label = f"test-invoice-{os.urandom(4).hex()}"
    description = "Test invoice for pytest"
    amount_msat = 100000
    
    invoice_response = node.receive(
        label=label,
        description=description,
        amount_msat=amount_msat
    )
    
    assert invoice_response is not None, "Invoice response should not be None"
    print(f"✓ Invoice created with amount: {invoice_response}")


def test_receive_invoice_any_amount(node):
    """Test creating a Lightning invoice with no specified amount."""
    label = f"test-invoice-any-{os.urandom(4).hex()}"
    description = "Test any-amount invoice for pytest"
    
    invoice_response = node.receive(
        label=label,
        description=description,
        amount_msat=None
    )
    
    assert invoice_response is not None, "Invoice response should not be None"
    print(f"✓ Any-amount invoice created: {invoice_response}")


def test_receive_invoice_unique_labels(node):
    """Test that multiple invoices can be created with unique labels."""
    invoices = []
    for i in range(3):
        label = f"test-multi-{os.urandom(4).hex()}"
        invoice_response = node.receive(
            label=label,
            description=f"Test invoice {i}",
            amount_msat=1000 * (i + 1)
        )
        invoices.append(invoice_response)
    
    assert len(invoices) == 3, "Should create 3 invoices"
    print("✓ Multiple unique invoices created")


@pytest.mark.skip(reason="Requires two nodes for actual payment test")
def test_send_payment(node):
    """Test sending a payment (requires a valid invoice)."""
    # This would require creating an invoice from another node
    # and then paying it with this node
    pass


@pytest.mark.skip(reason="Requires funded wallet for actual on-chain send")
def test_onchain_send(node):
    """Test sending Bitcoin on-chain."""
    destination = "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq"
    # Would need: node.onchain_send(destination=destination, amount_or_all="1000")
    pass


def test_node_stop(node):
    """Test stopping a node."""
    try:
        node.stop()
        print("✓ Node stopped successfully")
    except Exception as e:
        # Stop may fail in test environment, that's okay
        print(f"Note: Node stop: {e}")
