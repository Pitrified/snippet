from itertools import chain


def a_generator(n):
    """A generator can yield wherever is needed
    """
    yield -1

    for i in range(n):
        yield i * 2

    yield -1


def b_generator(n):
    """You can return a generator object
    """
    if n % 2 == 0:
        gen = helper_function_even(n)
        print(f"Type of gen {type(gen)}")
        return gen
    else:
        return helper_function_odd(n)


def c_generator(n):
    """To yield a combined result, use itertools.chain

    The order of execution is lazy, the helper_function is called when iterating
    """

    #  i1 = yield -1
    i1 = range(-1,1)
    i2 = helper_function_even(n)
    print(f"Type of i1 {type(i1)} i2 {type(i2)}")

    i_chain = chain(i1, i2)
    return i_chain


def helper_function_even(x):
    print(f"Helping even {x}")
    for i in range(x):
        yield i * 3


def helper_function_odd(x):
    print(f"Helping odd {x}")
    for i in range(x):
        yield i * 4
