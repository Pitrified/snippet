import pytest

from cursive_writer.utils.utils import iterate_double_list
from cursive_writer.utils.utils import enumerate_double_list


def test_iterate_double_list():
    the_list = [[0, 1, 2], [3, 4]]
    iterated = list(iterate_double_list(the_list))
    assert iterated[0] == 0
    assert iterated[2] == 2
    assert iterated[3] == 3
    assert iterated[4] == 4


def test_iterate_double_list_empty():
    the_list = []
    iterated = list(iterate_double_list(the_list))
    assert len(iterated) == 0


def test_enumerate_double_list():
    the_list = [[0, 1, 2], [3, 4]]
    enumerated = list(enumerate_double_list(the_list))
    assert enumerated[0] == (0, 0, 0)
    assert enumerated[2] == (0, 2, 2)
    assert enumerated[3] == (1, 0, 3)
    assert enumerated[4] == (1, 1, 4)


def test_enumerate_double_list_empty():
    the_list = []
    enumerated = list(enumerate_double_list(the_list))
    assert len(enumerated) == 0
