import logging
import numpy as np
from timeit import default_timer as timer

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn

def line_curve(x0, y0, x1, y1):
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


def collide_line_box(left, top, right, bot, line_coeff):
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
    logg.debug(f"{fmt_cn('Start', 'start')} collide_line_box")
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
