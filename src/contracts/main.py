from nagini_contracts.contracts import *


def div(a: int, b: int) -> int:
    Requires(b != 0)
    Ensures(Result() * b == a)
    return a // b


if __name__ == "__main__":
    div(1, 2)
