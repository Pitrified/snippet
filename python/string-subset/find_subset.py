"""Find if a string is a subset of another string."""


def is_subset(query: str, string: str) -> bool:
    """Check."""
    print(f"{query=} {string=}")
    start = 0
    for char in query:
        print(f"    {char=}")
        if char in string:
            # ix = string.index(char)
            ix = string.index(char, start)
            # print(f"   {char} at {ix} in {string}")
            print(f"        {char} at {ix} in {string}, will search {string[ix + 1 :]}")
            # string = string[ix + 1 :]
            # print(f"   now got {string=}")
        else:
            print(f"        missing {char}, fail.")
            return False
    return True


def main():
    """Run the main."""
    query = "abcd"
    str_list = [
        "abcd",
        "a0b0c0d0",
        "a0b0c0",
    ]

    for s in str_list:
        is_sub = is_subset(query, s)
        print(f"{query} is subset: {is_sub}")


if __name__ == "__main__":
    main()
