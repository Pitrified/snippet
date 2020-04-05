import logging


def iterate_double_list(the_list):
    """Iterate over the elements of a list of lists

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for inner_list in the_list:
        for element in inner_list:
            yield element


def enumerate_double_list(the_list):
    """Enumerate the content of a list of lists, providing both indexes

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for i, inner_list in enumerate(the_list):
        for j, element in enumerate(inner_list):
            yield i, j, element
