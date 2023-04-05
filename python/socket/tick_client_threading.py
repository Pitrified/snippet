from websockets.sync.client import connect


def hello() -> None:
    with connect("ws://localhost:8765") as websocket:
        for msg in websocket:
            print(f"<<< {msg}")


if __name__ == "__main__":
    hello()
