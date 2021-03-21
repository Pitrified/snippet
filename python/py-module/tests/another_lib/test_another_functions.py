import pytest

from sample.another_lib.another_functions import ListTracker


@pytest.fixture
def list_tracker():
    return ListTracker()


def test_new_list(list_tracker):
    l = [1, 2, -2]
    list_tracker.new_list(l)
    assert list_tracker.total == 1
    assert list_tracker.slow_total == 1
