from websockets.sync.server import serve, ServerConnection


def echo(websocket: ServerConnection) -> None:
    print("Waiting for message...")
    message = websocket.recv()
    print(f"Echoing: {message}")
    websocket.send(message)
    websocket.send('post scriptum')


def main() -> None:
    with serve(echo, "localhost", 8765) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
