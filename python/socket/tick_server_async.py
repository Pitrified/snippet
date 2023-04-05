#!/usr/bin/env python

"""A simple WebSocket echo server.

Run this script, then run hello_client.py.

https://websockets.readthedocs.io/en/stable/
"""

import asyncio
from websockets.server import serve, WebSocketServerProtocol


async def tick(websocket: WebSocketServerProtocol) -> None:
    print("Started ticking")
    print(f"{type(websocket)=}")
    for i in range(3):
        msg = f"Tick {i}"
        print("Awaiting send")
        print(f">>> {msg}")
        await websocket.send(msg)
        await asyncio.sleep(1)


async def main() -> None:
    async with serve(tick, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
