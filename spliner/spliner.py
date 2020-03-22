import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt
from random import seed as rseed
from timeit import default_timer as timer

from math import atan2
from math import degrees
from math import radians
from math import tan

import utils


class SPoint:
    def __init__(self, x, y, ori_deg):
        """Create a spline point

        point (x,y) with orientation yp in degrees, ranging [-180, 180]
        """
        self.x = x
        self.y = y
        self.ori_deg = ori_deg
        self.ori_rad = radians(self.ori_deg)
        self.ori_slo = tan(self.ori_rad)

    def __add__(self, other):
        """
        """
        r_x = self.x + other.x
        r_y = self.y + other.y
        r_ori = self.ori_deg + other.ori_deg
        if r_ori > 180:
            r_ori -= 360
        if r_ori < -180:
            r_ori += 360
        result = SPoint(r_x, r_y, r_ori)
        return result

    def __sub__(self, other):
        """
        """
        r_x = self.x - other.x
        r_y = self.y - other.y
        r_ori = self.ori_deg - other.ori_deg
        if r_ori > 180:
            r_ori -= 360
        if r_ori < -180:
            r_ori += 360
        result = SPoint(r_x, r_y, r_ori)
        return result

    def __repr__(self):
        the_repr_str = ""
        #  the_repr_str += f"x {self.x:.4f}"
        #  the_repr_str += f" y {self.y:.4f}"
        the_repr_str += f"({self.x:.4f}, {self.y:.4f})"
        the_repr_str += f" # {self.ori_deg:.4f}"
        return the_repr_str


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="hp.jpg",
        help="path to input image to use",
    )

    parser.add_argument(
        "-s", "--rand_seed", type=int, default=-1, help="random seed to use"
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')

    # example log line
    logg = logging.getLogger(f"c.{__name__}.setup_logger")
    logg.debug(f"Done setting up logger")


def setup_env():
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.rand_seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.rand_seed
    rseed(myseed)
    np.random.seed(myseed)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 prova_solver.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def compute_segment_points(x_start, x_end, coeff, num_samples=50):
    """Sample a poly_model in the [x_start, x_end] range
    """
    x_sample = np.linspace(x_start, x_end, num_samples)
    y_segment = utils.poly_model(x_sample, np.flip(coeff))
    return x_sample, y_segment


def cubic_curve(p0, p1):
    """Find the coefficient for a cubic curve passing through two points

    Tangents are the slope of the curve on the point
    p0 = (x0, y0) with tangent y0p
    p1 = (x1, y1) with tangent y1p

    y = a*x^3 + b*x^2 + c*x + d
    y' = 3*a*x^2 + 2*b*x + c

    Small tangent change is suggested to avoid deep min/max bedtween the points
    Both tangents should be smallish, in the [-1, 1] range
    """
    logg = logging.getLogger(f"c.{__name__}.cubic_curve")
    #  logg.debug(f"Starting cubic_curve")
    #  logg.setLevel("INFO")
    x0 = p0.x
    y0 = p0.y
    y0p = p0.ori_slo
    x1 = p1.x
    y1 = p1.y
    y1p = p1.ori_slo

    A = np.array(
        [
            [x0 ** 3, x0 ** 2, x0, 1],
            [3 * x0 ** 2, 2 * x0 ** 1, 1, 0],
            [x1 ** 3, x1 ** 2, x1, 1],
            [3 * x1 ** 2, 2 * x1 ** 1, 1, 0],
        ]
    )
    b = np.array([y0, y0p, y1, y1p])
    # x are the coefficients of the curve
    x = np.linalg.solve(A, b)

    #  logg.debug(f"x: {x}")
    logg.debug(f"y = {x[0]:.4f}*x^3 + {x[1]:.4f}*x^2 + {x[2]:.4f}*x + {x[3]:.4f}")

    return x


def cubic_curve_example():
    # create the plot
    fig, ax = plt.subplots()
    # sample per segment
    num_samples = 100

    # first segment
    p0 = SPoint(1, 1, 0)
    p1 = SPoint(3, 2, 45)
    # compute the coeff to fit the points
    coeff = cubic_curve(p0, p1)
    # add the segment
    x_sample, y_segment = compute_segment_points(p0.x, p1.x, coeff)
    utils.add_points(x_sample, y_segment, ax)

    # second segment
    p0 = SPoint(3, 2, 45)
    p1 = SPoint(3.5, 3.5, 80)
    coeff = cubic_curve(p0, p1)
    x_sample, y_segment = compute_segment_points(p0.x, p1.x, coeff)
    utils.add_points(x_sample, y_segment, ax, "r")

    # plot everything
    utils.plot_build(fig, ax)
    plt.show()


def compute_spline(p0, p1, num_samples=100):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.compute_spline")
    logg.debug(f"Starting compute_spline")

    # direction from point 0 to 1
    dir_01 = degrees(atan2(p1.y - p0.y, p1.x - p0.x))
    logg.debug(f"dir_01: {dir_01}")

    # rotate the point and translate them in the origin
    rot_p0 = SPoint(0, 0, p0.ori_deg - dir_01)
    # tranlsate p1 towards origin by p0
    tran_p1x = p1.x - p0.x
    tran_p1y = p1.y - p0.y
    # rotate p1 position by dir_01
    rototran_p1 = utils.rotate_point(np.array([tran_p1x, tran_p1y]), dir_01)
    rot_p1 = SPoint(rototran_p1[0], rototran_p1[1], p1.ori_deg - dir_01)
    logg.debug(f"rot_p0: {rot_p0} rot_p1: {rot_p1}")
    # plot the rotated vectors
    #  utils.add_vector(rot_p0, ax, color="r")
    #  utils.add_vector(rot_p1, ax, color="r")

    # compute the spline points
    coeff = cubic_curve(rot_p0, rot_p1)
    x_sample, y_segment = compute_segment_points(rot_p0.x, rot_p1.x, coeff)
    #  utils.add_points(x_sample, y_segment, ax, color="g")

    # rotate the points back
    all_segment = np.array([x_sample, y_segment]).transpose()
    logg.debug(f"all_segment.shape: {all_segment.shape}")
    rotated_segment = utils.rotate_point(all_segment, -dir_01)
    logg.debug(f"rotated_segment.shape: {rotated_segment.shape}")

    # translate them
    tran_segment = rotated_segment + np.array([p0.x, p0.y])
    tran_segment = tran_segment.transpose()
    logg.debug(f"tran_segment.shape: {tran_segment.shape}")
    rototran_x = tran_segment[0]
    rototran_y = tran_segment[1]

    return rototran_x, rototran_y


def example_spline():
    """
    """
    logg = logging.getLogger(f"c.{__name__}.example_spline")
    logg.debug(f"Starting example_spline")

    # create the plot
    fig, ax = plt.subplots()
    ax.set_xlim(0, 4)
    ax.set_ylim(-3, 4)

    # sample per segment
    num_samples = 100

    # first segment
    p0 = SPoint(1, 1, 30)
    #  p1 = SPoint(3, 2, 45)
    p1 = SPoint(2.6, 3, 60)
    logg.debug(f"p0: {p0} p1: {p1}")
    utils.add_vector(p0, ax, color="k")
    utils.add_vector(p1, ax, color="k")

    # compute the spline
    spline_x, spline_y = compute_spline(p0, p1)

    # plot the finished spline
    utils.add_points(spline_x, spline_y, ax, color="y")

    # plot everything
    utils.plot_build(fig, ax)
    plt.show()


def draw_long_spline(all_points, xlim, ylim):
    """
    """
    fig, ax = plt.subplots()
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    for i in range(len(all_points) - 1):
        p0 = all_points[i]
        p1 = all_points[i + 1]
        #  utils.add_vector(p0, ax, color="k", vec_len=20)

        spline_x, spline_y = compute_spline(p0, p1)
        utils.add_points(spline_x, spline_y, ax, color="y")

    #  utils.add_vector(p1, ax, color="k", vec_len=20)
    utils.plot_build(fig, ax)
    plt.show()


def example_long_spline():
    """
    """
    logg = logging.getLogger(f"c.{__name__}.example_long_spline")
    logg.debug(f"Starting example_long_spline")

    xlim = -4, 4
    ylim = -1, 7
    all_points = [
        SPoint(0, 0, 0),
        SPoint(2, 1, 45),
        SPoint(3, 3, 90),
        SPoint(2, 5, 135),
        SPoint(0, 6, 180),
        SPoint(-2, 5, -135),
        SPoint(-3, 3, -90),
        SPoint(-2, 1, -45),
        SPoint(0, 0, 0),
    ]
    #  draw_long_spline(all_points, xlim, ylim)
    all_points = [
        SPoint(0, 0, 0),
        SPoint(3, 3, 90),
        SPoint(0, 6, 180),
        SPoint(-3, 3, -90),
        SPoint(0, 0, 0),
    ]
    #  draw_long_spline(all_points, xlim, ylim)

    xlim = 0, 124
    ylim = -250, 0
    all_points = [
        SPoint(10, -223, 19),
        SPoint(36.5, -205.5, 43),
        SPoint(55.8, -181, 57.28),
        SPoint(68.5, -160, 61.09),
        SPoint(80.6, -136.5, 64),
        SPoint(94, -107.8, 66.3),
        SPoint(103, -85, 71),
        SPoint(109.6, -63, 77),
        SPoint(112.6, -48, 81),
        SPoint(113.8, -38.6, 88),
        SPoint(113.5, -32, 98),
        SPoint(111, -24.1, 115.6),
        SPoint(108.8, -21.4, 142),
        SPoint(106, -20, 164),
        SPoint(102.7, -19.6, 180),
        SPoint(97.2, -21, -153.7),
        SPoint(91.5, -24.8, -139),
        SPoint(84, -33, -127.85),
        SPoint(78.2, -41.2, -122.1),
        SPoint(67.5, -60.6, -117),
        SPoint(57, -84.8, -110.5),
        SPoint(47.8, -113, -104.85),
        SPoint(42, -137.5, -100.81),
        SPoint(38.7, -156, -97.7),
        SPoint(37, -172.6, -94.1),
        SPoint(36.2, -189.2, -91.7),
        SPoint(36.2, -199, -88.9),
        SPoint(37.8, -217.6, -80.9),
        SPoint(38.6, -221.9, -78.15),
        SPoint(40.4, -228, -66.22),
        SPoint(42.8, -231.9, -50.40),
        SPoint(45.3, -234, -33.24),
        SPoint(48.7, -235, -1.52),
        SPoint(52.8, -234.3, 18),
        SPoint(58, -231.2, 37.66),
        SPoint(64, -225.4, 48.75),
        SPoint(70, -217.8, 55),
        SPoint(77, -207.8, 58.4),
        SPoint(88, -189.5, 57.9),
    ]
    draw_long_spline(all_points, xlim, ylim)


if __name__ == "__main__":
    args = setup_env()
    #  cubic_curve_example()
    #  example_spline()
    example_long_spline()
