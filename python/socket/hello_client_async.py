"""Hello client using asyncio."""

import asyncio
from websockets.client import connect


async def hello():
    uri = "ws://localhost:8765"
    async with connect(uri) as websocket:
        # name = input("What's your name? ")
        name = "Hello world!"

        await websocket.send(name)
        print(f">>> {name}")

        greeting = await websocket.recv()
        print(f"<<< {greeting}")


if __name__ == "__main__":
    asyncio.run(hello())
