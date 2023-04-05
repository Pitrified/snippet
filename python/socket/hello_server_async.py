#!/usr/bin/env python

"""A simple WebSocket echo server.

Run this script, then run hello_client.py.

https://websockets.readthedocs.io/en/stable/
"""

import asyncio
from websockets.server import serve


async def echo(websocket) -> None:
    async for message in websocket:
        print(f"Received: {message}")
        await websocket.send(message)


async def main() -> None:
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
