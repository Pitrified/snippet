import numpy as np


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
