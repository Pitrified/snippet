import logging
import numpy as np

from pathlib import Path

from math import degrees
from math import radians
from math import cos
from math import sin

import spliner


def poly_model(x, beta):
    """Compute y values of a polynomial

    x: x vector
    beta: polynomial parameters
    """
    pol_order = len(beta)
    x_matrix = np.array([x ** i for i in range(pol_order)]).transpose()
    y_true = np.matmul(x_matrix, beta)
    return y_true


def add_points(x, y, ax, color="b"):
    #  ax.plot(x, y, color=color, ls="", marker=".")
    ax.plot(x, y, color=color, ls="-")


def add_segment(x_start, x_end, coeff, ax, num_samples=50, color="b"):
    x_sample = np.linspace(x_start, x_end, num_samples)
    y_segment = poly_model(x_sample, np.flip(coeff))
    add_points(x_sample, y_segment, ax, color=color)


def plot_build(fig, ax):
    """
    """
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid()
    #  ax.legend()
    fig.tight_layout()


def add_vector(sp, ax, color="b", vec_len=0.3):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.add_vector")
    logg.setLevel("INFO")
    #  logg.debug(f"Starting add_vector")

    head_width = 0.05 * vec_len
    head_length = 0.1 * vec_len
    end_x = cos(sp.ori_rad) * vec_len
    end_y = sin(sp.ori_rad) * vec_len
    logg.debug(f"sp {sp} end_x: {end_x} end_y: {end_y}")

    ax.arrow(
        sp.x,
        sp.y,
        end_x,
        end_y,
        head_width=head_width,
        head_length=head_length,
        fc=color,
        ec=color,
    )


def slope2deg(slope, direction=1):
    """Convert the slope of a line to an angle in degrees
    """
    return degrees(np.arctan2(slope, direction))


def slope2rad(slope, direction=1):
    """Convert the slope of a line to an angle in radians
    """
    return np.arctan2(slope, direction)


def compute_rot_matrix(theta):
    """Compute the rotation matrix for angle theta in degrees
    """
    logg = logging.getLogger(f"c.{__name__}.compute_rot_matrix")
    logg.setLevel("INFO")

    theta = radians(theta)
    ct = cos(theta)
    st = sin(theta)
    rot_mat = np.array(((ct, -st), (st, ct)))
    logg.debug(f"rot_mat = {rot_mat}")

    return rot_mat


def rotate_point(point, theta):
    """Rotate a point by theta degree
    """
    rot_mat = compute_rot_matrix(theta)
    return np.matmul(point, rot_mat)


def load_points(letter_file_path):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.load_points")
    logg.debug(f"Starting load_points")

    all_points = []

    with letter_file_path.open() as f:
        for line in f:
            pezzi = line.rstrip().split("\t")
            x = float(pezzi[0])
            y = float(pezzi[1])
            ori_deg = float(pezzi[2])
            point = spliner.SPoint(x, y, ori_deg)
            all_points.append(point)

    return all_points
