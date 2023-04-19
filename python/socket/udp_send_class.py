"""https://wiki.python.org/moin/UdpCommunication"""

import socket
from time import sleep
from typing import Self


class UdpSocketSender:
    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message: str) -> None:
        message_bytes = message.encode("utf-8")
        self.sock.sendto(message_bytes, (self.ip, self.port))

    def quit(self) -> None:
        self.send("quit")

    def __exit__(self, exc_type, exc_value, traceback):
        self.quit()

    def __enter__(self) -> Self:
        return self


def main() -> None:
    """Show the use of the UdpSocketSender class."""
    # host and port
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    with UdpSocketSender(UDP_IP, UDP_PORT) as uss:
        for i in range(3):
            MESSAGE = f"Hello, World! {i}"
            print(f"sending: {MESSAGE}")
            uss.send(MESSAGE)
            sleep(0.1)


if __name__ == "__main__":
    main()
