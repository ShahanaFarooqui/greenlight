class TlsConfig:
    def __init__(self) -> None: ...
    def with_ca_certificate(self, ca: bytes) -> "TlsConfig": ...
    def identity(self, cert_pem: bytes, key_pem: bytes) -> "TlsConfig": ...

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

class Scheduler:
    def __init__(self, node_id: bytes, network: str): ...
    def register(self, signer: Signer) -> bytes: ...
    def recover(self, signer: Signer) -> bytes: ...
    def get_node_info(self) -> bytes: ...
    def schedule(self) -> bytes: ...

class Node:
    def __init__(self, node_id: bytes, network: str, tls: TlsConfig, grpc_uri: str) -> None: ...
    def stop(self) -> None: ...
    def call(self, method: str, request: bytes) -> bytes: ...
