# in python 3.7 use this and there is no need for the string literal
# from __future__ import annotations


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, other) -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __repr__(self) -> str:
        return f"{(self.x, self.y)}"


def run_mypy_add() -> None:
    a = Point(0, 1)
    b = Point(2, 3)
    print(f"a + b = {a+b}")

    # will be marked as error by mypy
    c: int = 0
    c = a + b
    print(f"a + b = {c}")


if __name__ == "__main__":
    run_mypy_add()
