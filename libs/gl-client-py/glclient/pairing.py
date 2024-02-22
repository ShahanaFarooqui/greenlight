from . import TlsConfig
from . import scheduler_pb2 as schedpb
import glclient.glclient as native
from typing import Optional, Generator


class NewDeviceClient(object):
    """A Pairing Client for the "new device" flow."""

    def __init__(self, tls: TlsConfig, uri: Optional[str] = None):
        self._inner = native.NewDeviceClient(tls=tls.inner, uri=uri)

    def _recv(self, m):
        msgs = {
            1: schedpb.PairDeviceResponse,
        }

        typ, msg = m[0], m[1:]
        conv = msgs.get(typ, None)

        if conv is None:
            raise ValueError(f"Unknown message type {typ}")

        yield conv.FromString(bytes(msg))

    def pair_device(
        self, name: str, description: str, restrictions: str
    ) -> Generator[schedpb.PairDeviceResponse, None, None]:
        """Starts a new paring session and yields for next message.

        First message would be the "QRData" data that must be presented to
        the attestation device.

        Second message is either the pairing response or an error.
        """
        for m in self._inner.pair_device(name, description, restrictions):
            yield from self._recv(m)
