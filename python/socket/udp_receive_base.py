"""https://wiki.python.org/moin/UdpCommunication"""

import socket


def main() -> None:
    """Simple UDP receiver."""

    # host and port
    UDP_IP = "127.0.0.1"
    UDP_PORT = 5005

    # create a socket object
    sock = socket.socket(
        socket.AF_INET,  # Internet
        socket.SOCK_DGRAM,  # UDP
    )
    sock.bind((UDP_IP, UDP_PORT))

    # buffer size is in bytes
    buffer_size = 1024

    while True:
        data_bytes, addr = sock.recvfrom(buffer_size)
        data = data_bytes.decode("utf-8")
        print(f"received message: {data}")
        print(f"            from: {addr}")

        if data == "quit":
            break


if __name__ == "__main__":
    main()
