import pytest

from sample.some_lib.some_functions import list_slow_add
from sample.some_lib.some_functions import list_good_add


def test_list_slow_add():
    res = list_slow_add([1, 2, -2])
    assert res == 1


def test_list_good_add():
    res = list_good_add([1, 2, -2])
    assert res == 1
