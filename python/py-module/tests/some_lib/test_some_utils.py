import pytest

from sample.some_lib.some_utils import slow_add
from sample.some_lib.some_utils import good_add


@pytest.mark.parametrize("a,b,expected", [(5, 5, 10), (0, 0, 0), (5, -3, 2)])
def test_slow_add(a, b, expected):
    assert slow_add(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [(5, 5, 10), (0, 0, 0), (5, -3, 2)])
def test_good_add(a, b, expected):
    assert good_add(a, b) == expected
