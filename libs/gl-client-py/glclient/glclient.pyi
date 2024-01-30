"""Stubs for the API exposed by the Rust `gl-client` library.

These refer to the API exposed by the Rust library, not the main
`glclient` python package. As such these mostly just concern the lower
level API that shuffles bytes back and forth. The `glclient` python
package adds a pythonic facade on top of this to improve usability.

"""

from typing import Optional, List
import glclient.glclient as native;


class TlsConfig:
    def __init__(self) -> None: ...
    def with_ca_certificate(self, ca: bytes) -> "TlsConfig": ...
    def identity(self, cert_pem: bytes, key_pem: bytes) -> "TlsConfig": ...
    def identity_from_path(self, path : str) -> "TlsConfig": ...

class CBuilder:
    def __init__(self): ...
    @staticmethod
    def from_bytes(data: bytes) -> CBuilder: ...
    @staticmethod
    def from_path(path: str) -> CBuilder: ...
    @staticmethod
    def from_pems(cert: bytes, key: bytes, ca: bytes) -> CBuilder: ...
    def with_rune(self, rune: str) -> CBuilder: ...
    def upgrade(self, scheduler: Scheduler, signer: Signer) -> CBuilder: ...
    def build(self) -> Credentials: ...

class DeviceBuilder:
    def __init__(self): ...
    def from_path(self, path: str) -> DeviceBuilder: ...
    def from_bytes(self, data: bytes) -> DeviceBuilder: ...
    def with_identity(self, cert: bytes, key: bytes) -> DeviceBuilder: ...
    def with_ca(self, ca: bytes) -> DeviceBuilder: ...
    def with_rune(self, rune: str) -> DeviceBuilder: ...
    def upgrade(self, scheudler: native.Scheduler, signer: native.Signer) -> DeviceBuilder: ...
    def build(self) -> Credentials: ...

class NobodyBuilder:
    def __init__(self): ...
    def with_default(self) -> NobodyBuilder: ...
    def with_identity(self, cert: bytes, key: bytes) -> NobodyBuilder: ...
    def with_ca(self, ca: bytes) -> NobodyBuilder: ...
    def build(self) -> Credentials: ...

class Credentials:
    @staticmethod
    def as_device() -> DeviceBuilder: ...
    @staticmethod
    def as_nobody() -> NobodyBuilder: ...
    def tls_config(self) -> TlsConfig: ...
    def rune(self) -> str: ...
    def to_bytes(self) -> bytes: ...

class SignerHandle:
    def shutdown(self) -> None: ...


class Signer:
    def __init__(self, secret: bytes, network: str, tls: TlsConfig): ...
    def sign_challenge(self, challenge: bytes) -> bytes: ...
    def run_in_thread(self) -> SignerHandle: ...
    def run_in_foreground(self) -> None: ...
    def node_id(self) -> bytes: ...
    def version(self) -> str: ...
    def is_running(self) -> bool: ...
    def shutdown(self) -> None: ...
    def create_rune(self, restrictions: List[List[str]], rune: Optional[str] = None) -> str: ...


class Scheduler:
    def __init__(self, node_id: bytes, network: str, tls: TlsConfig): ...
    def register(self, signer: Signer, invite_code: Optional[str]) -> bytes: ...
    def recover(self, signer: Signer) -> bytes: ...
    def get_node_info(self) -> bytes: ...
    def schedule(self) -> bytes: ...
    def export_node(self) -> bytes: ...
    def get_invite_codes(self) -> bytes: ...
    def add_outgoing_webhook(self, uri: str) -> bytes: ...
    def list_outgoing_webhooks(self) -> bytes: ...
    def delete_outgoing_webhook(self, webhook_id: int) -> bytes: ...
    def delete_outgoing_webhooks(self, webhook_ids: List[int]) -> bytes: ...
    def rotate_outgoing_webhook_secret(self, webhook_id: int)  -> bytes: ...


class Node:
    def __init__(
        self,
        node_id: bytes,
        network: str,
        grpc_uri: str,
        creds: Credentials,
    ) -> None: ...
    def stop(self) -> None: ...
    def call(self, method: str, request: bytes) -> bytes: ...
    def get_lsp_client(self) -> LspClient: ...
    def configure(self, payload: bytes) -> None: ...

class LspClient:
    def rpc_call(self, peer_id: bytes, method: str, params: bytes) -> bytes: ...
    def rpc_call_with_json_rpc_id(
        self,
        peer_id: bytes,
        method: str,
        params: bytes,
        json_rpc_id: Optional[str] = None,
    ) -> bytes: ...
    def list_lsp_servers(self) -> List[str]: ...


def backup_decrypt_with_seed(encrypted: bytes, seed: bytes) -> bytes: ...
