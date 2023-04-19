"""https://wiki.python.org/moin/UdpCommunication"""

import socket
from time import sleep


def main() -> None:
    """Simple UDP sender."""

    # host and port
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005
    print(f"UDP target IP: {UDP_IP}")
    print(f"UDP target port: {UDP_PORT}")

    # create a socket object
    sock = socket.socket(
        socket.AF_INET,  # Internet
        socket.SOCK_DGRAM,  # UDP
    )

    # send a bunch of messages
    for i in range(3):
        MESSAGE = f"Hello, World! {i}"
        print(f"sending: {MESSAGE}")
        MESSAGE_BYTES = MESSAGE.encode("utf-8")
        sock.sendto(MESSAGE_BYTES, (UDP_IP, UDP_PORT))
        sleep(0.1)

    MESSAGE_BYTES = "quit".encode("utf-8")
    sock.sendto(MESSAGE_BYTES, (UDP_IP, UDP_PORT))


if __name__ == "__main__":
    main()
