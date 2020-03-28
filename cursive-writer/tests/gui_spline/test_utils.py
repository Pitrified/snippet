import pytest

from cursive_writer.utils.geometric_utils import collide_line_box


@pytest.mark.parametrize(
    "left, top, right, bot, line_coeff, expected",
    [(10, 5, 20, 15, [0, 10], [(10, 10), (20, 10)]), (10, 5, 20, 15, [0, 20], []),],
)
def test_horizontal(left, top, right, bot, line_coeff, expected):
    admissible_inter = collide_line_box(left, top, right, bot, line_coeff)
    assert admissible_inter == expected


@pytest.mark.parametrize(
    "left, top, right, bot, line_coeff, expected",
    [
        (10, 5, 20, 15, [float("inf"), 17], [(17, 5), (17, 15)]),
        (10, 5, 20, 15, [float("inf"), 5], []),
    ],
)
def test_vertical(left, top, right, bot, line_coeff, expected):
    admissible_inter = collide_line_box(left, top, right, bot, line_coeff)
    assert admissible_inter == expected


@pytest.mark.parametrize(
    "left, top, right, bot, line_coeff, expected",
    [
        (10, 5, 20, 15, [1, 0], [(10, 10), (15, 15)]),
        (10, 5, 20, 15, [1, -10], [(15, 5), (20, 10)]),
        (10, 5, 20, 15, [-1, 20], [(10, 10), (15, 5)]),
        (10, 5, 20, 15, [-1, 30], [(20, 10), (15, 15)]),
    ],
)
def test_diagonal(left, top, right, bot, line_coeff, expected):
    admissible_inter = collide_line_box(left, top, right, bot, line_coeff)
    assert admissible_inter == expected
