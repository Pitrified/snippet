import numpy as np
import math


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
    """
    """
    #  ax.plot(x, y, color=color, ls="", marker=".")
    ax.plot(x, y, color=color, ls="-")


def plot_build(fig, ax):
    """
    """
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid()
    ax.legend()
    fig.tight_layout()


def slope2deg(slope, direction=1):
    """Convert the slope of a line to an angle in degrees
    """
    return rad2deg(np.arctan2(slope, direction))


def slope2rad(slope, direction=1):
    """Convert the slope of a line to an angle in radians
    """
    return np.arctan2(slope, direction)


def deg2rad(deg):
    """
    """
    return deg * math.pi / 180


def rad2deg(deg):
    """
    """
    return rad * 180 / math.pi
