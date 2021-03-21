import pytest
from pytest import approx

from cursive_writer.utils.geometric_utils import collide_line_box
from cursive_writer.utils.oriented_point import OrientedPoint


@pytest.mark.parametrize(
    "bbox, line_point, expected",
    [
        ((10, 5, 20, 15), OrientedPoint(0, 10, 0), [(10, 10), (20, 10)]),
        ((10, 5, 20, 15), OrientedPoint(0, 20, 0), []),
    ],
)
def test_horizontal(bbox, line_point, expected):
    admissible_inter = collide_line_box(bbox, line_point)
    if len(expected) == 0:
        assert admissible_inter == expected
    else:
        assert admissible_inter[0] == approx(expected[0])
        assert admissible_inter[1] == approx(expected[1])


@pytest.mark.parametrize(
    "bbox, line_point, expected",
    [
        ((10, 5, 20, 15), OrientedPoint(17, 0, 90), [(17, 5), (17, 15)]),
        ((10, 5, 20, 15), OrientedPoint(5, 0, 90), []),
    ],
)
def test_vertical(bbox, line_point, expected):
    admissible_inter = collide_line_box(bbox, line_point)
    if len(expected) == 0:
        assert admissible_inter == expected
    else:
        assert admissible_inter[0] == approx(expected[0])
        assert admissible_inter[1] == approx(expected[1])


@pytest.mark.parametrize(
    "bbox, line_point, expected",
    [
        ((10, 5, 20, 15), OrientedPoint(0, 0, 45), [(10, 10), (15, 15)]),
        ((10, 5, 20, 15), OrientedPoint(0, -10, 45), [(15, 5), (20, 10)]),
        ((10, 5, 20, 15), OrientedPoint(0, 20, -45), [(10, 10), (15, 5)]),
        ((10, 5, 20, 15), OrientedPoint(0, 30, -45), [(20, 10), (15, 15)]),
    ],
)
def test_diagonal(bbox, line_point, expected):
    admissible_inter = collide_line_box(bbox, line_point)
    if len(expected) == 0:
        assert admissible_inter == expected
    else:
        assert admissible_inter[0] == approx(expected[0])
        assert admissible_inter[1] == approx(expected[1])
