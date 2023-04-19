"""https://wiki.python.org/moin/UdpCommunication"""

import socket
from typing import Any, Generator, Self, TypeAlias

# from socket import _RetAddress
_RetAddress: TypeAlias = Any


class UdpSocketReceiver:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))

    def receive(
        self,
        buffer_size: int,
    ) -> Generator[tuple[str, _RetAddress], None, None]:
        while True:
            data, addr = self.receive_once(buffer_size)
            if data == "quit":
                return
            yield data, addr

    def receive_once(self, buffer_size: int) -> tuple[str, _RetAddress]:
        data_bytes, addr = self.sock.recvfrom(buffer_size)
        data = data_bytes.decode("utf-8")
        return data, addr

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self) -> None:
        print("closing socket")
        self.sock.close()


def main() -> None:
    """Show the use of the UdpSocketReceiver class."""

    # host and port
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    # buffer size is in bytes
    buffer_size = 1024

    # use as a context manager
    # when we receive the quit message, we exit the context manager
    with UdpSocketReceiver(UDP_IP, UDP_PORT) as usr:
        for data, addr in usr.receive(buffer_size):
            print(f"received message: {data}")
            print(f"            from: {addr}")

    # use as a regular object
    # we can receive unlimited messages, ignoring the quit message
    usr = UdpSocketReceiver(UDP_IP, UDP_PORT)
    try:
        while True:
            data, addr = usr.receive_once(buffer_size)
            print(f"received message: {data}")
            print(f"            from: {addr}")
    except KeyboardInterrupt:
        pass
    finally:
        usr.close()


if __name__ == "__main__":
    main()
