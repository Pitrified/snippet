import logging
import math


def plot_build(fig, ax):
    """"""
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid()
    #  ax.legend()
    fig.tight_layout()


def add_vector(sp, ax, color="b", vec_len=0.3):
    """Add a point with direction to the plot"""
    logg = logging.getLogger(f"c.{__name__}.add_vector")
    logg.setLevel("INFO")
    #  logg.debug(f"Starting add_vector")

    head_width = 0.05 * vec_len
    head_length = 0.1 * vec_len
    end_x = math.cos(sp.ori_rad) * vec_len
    end_y = math.sin(sp.ori_rad) * vec_len
    logg.debug(f"sp {sp} end_x: {end_x} end_y: {end_y}")

    # plot this invisible point so that the ax limits update correctly
    ax.plot(sp.x, sp.y, color="g", ls="", marker="")

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
