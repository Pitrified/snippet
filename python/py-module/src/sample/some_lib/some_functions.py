# relative import: some_utils is in the same folder, so this is enough
from .some_utils import slow_add

# absolute import: the top level is sample, specify folder structure
from sample.some_lib.some_utils import good_add


def list_slow_add(l):
    """Slowly adds the elements in the list l

    :l: input list
    :returns: the sum of the elements

    """
    total = 0
    for e in l:
        total = slow_add(total, e)
    return total


def list_good_add(l):
    """Add the elements in the list l

    :l: input list
    :returns: the sum of the elements

    """
    total = 0
    for e in l:
        total = good_add(total, e)
    return total
