"""Hello client using asyncio."""

import asyncio
from loguru import logger as lg
from websockets.client import connect


async def listen():
    uri = "ws://localhost:8765"
    async with connect(uri) as websocket:
        async for msg in websocket:
            print("Awaiting receive")
            print(f"<<< {msg}")


if __name__ == "__main__":
    asyncio.run(listen())
