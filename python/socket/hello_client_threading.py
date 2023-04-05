#!/usr/bin/env python

"""A simple client that connects to a server and sends a message.

Run hello_server.py first.

https://websockets.readthedocs.io/en/stable/
"""

import asyncio
from websockets.sync.client import connect


def hello() -> None:
    with connect("ws://localhost:8765") as websocket:
        print("Connected")
        websocket.send("Hello world!")
        print("Waiting for response...")
        message = websocket.recv()
        print(f"Received: {message}")
        message = websocket.recv()
        print(f"Received: {message}")


if __name__ == "__main__":
    hello()
