import logging
import numpy as np
from timeit import default_timer as timer

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.oriented_point import OrientedPoint

from math import degrees
from math import radians
from math import atan2
from math import sqrt
from math import cos
from math import sin


def line_curve_ab_coeff(x0, y0, x1, y1):
    """Find the coefficient for a linear curve passing through two points

    y = ax + b
    """
    logg = logging.getLogger(f"c.{__name__}.line_curve")
    logg.setLevel("INFO")
    logg.debug(f"{fmt_cn('Starting', 'start')} line_curve")

    if x1 == x0:
        return [float("inf"), x0]

    a = (y1 - y0) / (x1 - x0)
    b = y0 - a * x0

    logg.debug(f"y = {a:.4f}*x + {b:.4f}")

    return [a, b]


def line_curve_point(x0, y0, x1, y1):
    """Find a point on the line with appropriate orientation
    """
    ori_deg = degrees(atan2(y1 - y0, x1 - x0))
    return OrientedPoint(x0, y0, ori_deg)


def collide_line_box(bbox, line_point):
    """Collide a line with a rectangular box

    line_coeff = [a, b]
    y = ax + b

          top
          ---
    left |   | right
         |   |
          ---
         bottom

    Note that the y axis is reversed in tkinter
    """
    logg = logging.getLogger(f"c.{__name__}.collide_line_box")
    logg.setLevel("INFO")
    logg.debug(f"{fmt_cn('Start', 'start')} collide_line_box")

    left, top, right, bot = bbox
    line_coeff = line_point.to_ab_line()
    logg.debug(f"left: {left} top: {top} right: {right} bot: {bot} coeff: {line_coeff}")

    a = line_coeff[0]
    b = line_coeff[1]
    # horizontal line
    if a == 0:
        if top < b < bot:
            logg.debug(f"Horizontal top: {top} b: {b} bot: {bot}")
            left_inter = (left, b)
            right_inter = (right, b)
            return [left_inter, right_inter]
        else:
            logg.debug(f"Horizontal outside")
            return []

    # vertical line
    elif a == float("inf"):
        if left < b < right:
            logg.debug(f"Vertical left: {left} b: {b} right: {right}")
            top_inter = (b, top)
            bot_inter = (b, bot)
            return [top_inter, bot_inter]
        else:
            logg.debug(f"Vertical outside")
            return []

    # regular line, find intersections
    left_inter = (left, a * left + b)
    top_inter = ((top - b) / a, top)
    right_inter = (right, a * right + b)
    bot_inter = ((bot - b) / a, bot)
    logg.debug(
        f"Intersections left: {left_inter} top: {top_inter} right: {right_inter} bot: {bot_inter}"
    )

    # more readable tuple coefficient
    x, y = 0, 1
    # select admissible intersections
    admissible_inter = []
    if top < left_inter[y] < bot:
        logg.debug(f"top < left_inter < bot")
        admissible_inter.append(left_inter)
    if left < top_inter[x] < right:
        logg.debug(f"left < top_inter < right")
        admissible_inter.append(top_inter)
    if top < right_inter[y] < bot:
        logg.debug(f"top < right_inter < bot")
        admissible_inter.append(right_inter)
    if left < bot_inter[x] < right:
        logg.debug(f"left < bot_inter < right")
        admissible_inter.append(bot_inter)

    return admissible_inter


def translate_line(line_coeff, shift_x, shift_y):
    """Translate a line by changing the b coeff

    y = ax + b
    Remember that tkinter has y axis toward the bottom
    """
    logg = logging.getLogger(f"c.{__name__}.translate_line")
    #  logg.setLevel("INFO")
    logg.debug(
        f"{fmt_cn('Starting', 'start')} translate_line {line_coeff} {shift_x} {shift_y}"
    )

    a, b = line_coeff

    b += shift_y
    b += -a * shift_x

    logg.debug(f"shifted: {[a, b]}")

    return [a, b]


def translate_point_dxy(orig_point, shift_x, shift_y):
    """Translate the orig_point of dx, dy and return a new one
    """
    return OrientedPoint(
        orig_point.x + shift_x, orig_point.y + shift_y, orig_point.ori_deg
    )


def translate_point_dir(orig_point, dir_deg, shift):
    """Translate the point along a direction of a certain amount
    """
    new_x = orig_point.x + shift * cos(radians(dir_deg))
    new_y = orig_point.y + shift * sin(radians(dir_deg))
    return OrientedPoint(new_x, new_y, orig_point.ori_deg)


def dist2D(p0, p1):
    """Distance between two points
    """
    return sqrt((p0.x - p1.x) ** 2 + (p0.y - p1.y) ** 2)
