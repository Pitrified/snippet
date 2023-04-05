import time
from websockets.sync.server import serve, ServerConnection


def tick(websocket: ServerConnection) -> None:
    for i in range(3):
        msg = f"Tick {i}"
        websocket.send(msg)
        time.sleep(0.91)


def main() -> None:
    with serve(tick, "localhost", 8765) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
