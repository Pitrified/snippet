import argparse
import logging
import numpy as np
import matplotlib.pyplot as plt

from random import seed as rseed
from timeit import default_timer as timer
from math import cos
from math import sin

from cursive_writer.spliner.spliner import fit_cubic
from cursive_writer.spliner.spliner import compute_cubic_segment
from cursive_writer.spliner.spliner import compute_thick_spline
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils import plot_utils


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

    addLoggingLevel("TRACE", 5)


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            # Yes, logger takes its '*args' as 'args'
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


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
    recap = f"python3 spliner_examples.py"
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
    if x_start > x_end:
        x_start, x_end = x_end, x_start

    x_sample = np.linspace(x_start, x_end, num_samples)
    y_segment = poly_model(x_sample, np.flip(coeff))
    return x_sample, y_segment


def ex_fit_cubic_curve():
    """
    """
    # create the plot
    fig, ax = plt.subplots()
    # sample per segment
    num_samples = 100

    # first segment
    p0 = OrientedPoint(1, 1, 0)
    p1 = OrientedPoint(3, 2, 45)
    # compute the coeff to fit the points
    coeff = fit_cubic(p0, p1)
    # add the segment
    x_sample, y_segment = compute_segment_points(p0.x, p1.x, coeff)
    ax.plot(x_sample, y_segment, color="b", ls="-", marker="")

    # second segment
    p0 = OrientedPoint(3, 2, 45)
    p1 = OrientedPoint(3.5, 3.5, 80)
    coeff = fit_cubic(p0, p1)
    x_sample, y_segment = compute_segment_points(p0.x, p1.x, coeff)
    ax.plot(x_sample, y_segment, color="r", ls="-", marker="")

    # plot everything
    plot_utils.plot_build(fig, ax)


def ex_compute_cubic_segment():
    """
    """
    logg = logging.getLogger(f"c.{__name__}.ex_compute_cubic_segment")
    logg.setLevel("DEBUG")
    logg.debug(f"Starting ex_compute_cubic_segment")

    # create the plot
    fig, ax = plt.subplots()
    #  ax.set_xlim(0, 4)
    #  ax.set_ylim(-3, 4)

    # sample per segment
    #  num_samples = 100

    # first segment
    p0 = OrientedPoint(10, 10, 30)
    #  p1 = OrientedPoint(3, 2, 45)
    p1 = OrientedPoint(26, 30, 60)
    logg.debug(f"p0: {p0} p1: {p1}")
    # plot the points
    plot_utils.add_vector(p0, ax, color="k", vec_len=3)
    plot_utils.add_vector(p1, ax, color="k", vec_len=3)

    # compute the spline
    spline_x, spline_y = compute_cubic_segment(p0, p1, ax=ax)

    # plot the finished spline
    ax.plot(spline_x, spline_y, color="y")

    # plot everything
    plot_utils.plot_build(fig, ax)


def ex_thick_spline(p0, p1, thickness, scale):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.ex_thick_spline")
    # logg.stLevel("INFO")
    logg.debug(f"\nStarting ex_thick_spline")

    logg.debug(f"p0: {p0} p1: {p1}")

    # create the plot
    fig, ax = plt.subplots()
    # ax.set_xlim(-2 * scale, 5 * scale)
    # ax.set_ylim(-3 * scale, 5 * scale)
    # ax.set_xlim(-1 * scale, 1.5 * scale)
    # ax.set_ylim(-2.5 * scale, 2.5 * scale)

    # compute the spline
    spline_x, spline_y = compute_thick_spline(p0, p1, thickness, ax=ax)
    # spline_x, spline_y = compute_thick_spline(p0, p1, thickness)

    # plot the finished spline
    ax.plot(spline_x, spline_y, color="k", marker=".", ls="")

    # plot everything
    plot_utils.plot_build(fig, ax)


def exs_thick_spline():
    """
    """
    # spline thickness
    thickness = 20
    scale = 10
    plot_scale = 10

    # this point with thickness 20 shows where the error is: the left/right
    # segment cross each other so the bottom spline has less points than left
    # segment + top spline + right segment
    p0 = OrientedPoint(0, 0, -10)
    p1 = OrientedPoint(2, 1, 35)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    p0 = OrientedPoint(1, 1, 45)
    p1 = OrientedPoint(4, 2, -45)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    p0 = OrientedPoint(1, 1, 55)
    p1 = OrientedPoint(2, 2, 65)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    p0 = OrientedPoint(1, 1, 25)
    p1 = OrientedPoint(2, 2, 35)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    # both segments are vertical
    p0 = OrientedPoint(1, 1, 45)
    p1 = OrientedPoint(2, 2, 45)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    # one of the segments is vertical
    p0 = OrientedPoint(1, 1, 45)
    p1 = OrientedPoint(4, 4, 55)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    # regular cases
    p0 = OrientedPoint(1 * scale, 1 * scale, 30)
    p1 = OrientedPoint(3 * scale, 3 * scale, 60)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    p0 = OrientedPoint(1 * scale, 1 * scale, 45)
    p1 = OrientedPoint(3 * scale, 2 * scale, 45)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    p0 = OrientedPoint(1 * scale, 1 * scale, -45)
    p1 = OrientedPoint(3 * scale, 2 * scale, -45)
    ex_thick_spline(p0, p1, thickness, plot_scale)

    p0 = OrientedPoint(1 * scale, 1 * scale, 45)
    p1 = OrientedPoint(4 * scale, 2 * scale, -45)
    ex_thick_spline(p0, p1, thickness, plot_scale)


def run_spliner_examples(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_spliner_examples")
    logg.debug(f"Starting run_spliner_examples")

    # ex_fit_cubic_curve()
    # ex_compute_cubic_segment()
    exs_thick_spline()

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_spliner_examples(args)
