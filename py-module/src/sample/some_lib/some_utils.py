def slow_add(x, y):
    """Slowly implemented sum operation

    :x: first operand
    :y: second operand
    :returns: the sum

    """
    if y >= 0:
        for _ in range(y):
            x += 1
    else:
        for _ in range(-y):
            x -= 1
    return x


def good_add(x, y):
    """Regular sum operation

    :x: first operand
    :y: second operand
    :returns: the sum

    """
    return x + y
