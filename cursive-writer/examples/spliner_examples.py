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
from cursive_writer.spliner.spliner import compute_long_spline
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


def ex_thick_spline(p0, p1, thickness):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.ex_thick_spline")
    # logg.stLevel("INFO")
    logg.debug(f"\nStarting ex_thick_spline")

    logg.debug(f"p0: {p0} p1: {p1}")

    # create the plot
    fig, ax = plt.subplots()

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
    scale = 10

    # these broke something
    thickness = 10
    p0 = OrientedPoint(438.5817, 508.1890, -174.7626)
    p1 = OrientedPoint(470.1365, 509.9414, -174.4506)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(347.9917, 485.3683, 178.4224)
    p1 = OrientedPoint(380.3771, 486.2859, -158.1566)
    ex_thick_spline(p0, p1, thickness)
    return

    # spline thickness
    thickness = 20

    # this point with thickness 20 shows where the error is: the left/right
    # segment cross each other so the bottom spline has less points than left
    # segment + top spline + right segment
    p0 = OrientedPoint(0, 0, -10)
    p1 = OrientedPoint(2, 1, 35)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(1, 1, 45)
    p1 = OrientedPoint(4, 2, -45)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(1, 1, 55)
    p1 = OrientedPoint(2, 2, 65)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(1, 1, 25)
    p1 = OrientedPoint(2, 2, 35)
    ex_thick_spline(p0, p1, thickness)

    # both segments are vertical
    p0 = OrientedPoint(1, 1, 45)
    p1 = OrientedPoint(2, 2, 45)
    ex_thick_spline(p0, p1, thickness)

    # one of the segments is vertical
    p0 = OrientedPoint(1, 1, 45)
    p1 = OrientedPoint(4, 4, 55)
    ex_thick_spline(p0, p1, thickness)

    # regular cases
    p0 = OrientedPoint(1 * scale, 1 * scale, 30)
    p1 = OrientedPoint(3 * scale, 3 * scale, 60)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(1 * scale, 1 * scale, 45)
    p1 = OrientedPoint(3 * scale, 2 * scale, 45)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(1 * scale, 1 * scale, -45)
    p1 = OrientedPoint(3 * scale, 2 * scale, -45)
    ex_thick_spline(p0, p1, thickness)

    p0 = OrientedPoint(1 * scale, 1 * scale, 45)
    p1 = OrientedPoint(4 * scale, 2 * scale, -45)
    ex_thick_spline(p0, p1, thickness)


def ex_long_spline(spline_sequence, thickness):
    """
    """
    fig, ax = plt.subplots()

    spline_samples = compute_long_spline(spline_sequence, thickness)

    for glyph in spline_samples:
        for segment in glyph:
            ax.plot(*segment, color="k", marker=".", ls="")

    # plot everything
    plot_utils.plot_build(fig, ax)


def exs_long_spline():
    """
    """
    thickness = 2
    spline_sequence = [
        [
            OrientedPoint(0, 0, 0),
            OrientedPoint(2, 1, 45),
            OrientedPoint(3, 3, 90),
            OrientedPoint(2, 5, 135),
            OrientedPoint(0, 6, 180),
            OrientedPoint(-2, 5, -135),
            OrientedPoint(-3, 3, -90),
            OrientedPoint(-2, 1, -45),
            OrientedPoint(0, 0, 0),
        ]
    ]
    ex_long_spline(spline_sequence, thickness)

    thickness = 10
    spline_sequence = [
        [
            OrientedPoint(00, 00, 0),
            OrientedPoint(20, 10, 45),
            OrientedPoint(30, 30, 90),
            OrientedPoint(20, 50, 135),
            OrientedPoint(00, 60, 180),
            OrientedPoint(-20, 50, -135),
            OrientedPoint(-30, 30, -90),
            OrientedPoint(-20, 10, -45),
            OrientedPoint(00, 00, 0),
        ]
    ]
    ex_long_spline(spline_sequence, thickness)

    thickness = 20
    spline_sequence = [
        [
            OrientedPoint(000, 000, 0),
            OrientedPoint(200, 100, 45),
            OrientedPoint(300, 300, 90),
            OrientedPoint(200, 500, 135),
            OrientedPoint(000, 600, 180),
            OrientedPoint(-200, 500, -135),
            OrientedPoint(-300, 300, -90),
            OrientedPoint(-200, 100, -45),
            OrientedPoint(000, 000, 0),
        ]
    ]
    ex_long_spline(spline_sequence, thickness)

    thickness = 5
    spline_sequence = [
        [
            OrientedPoint(10, -223, 19),
            OrientedPoint(36.5, -205.5, 43),
            OrientedPoint(55.8, -181, 57.28),
            OrientedPoint(68.5, -160, 61.09),
            OrientedPoint(80.6, -136.5, 64),
            OrientedPoint(94, -107.8, 66.3),
            OrientedPoint(103, -85, 71),
            OrientedPoint(109.6, -63, 77),
            OrientedPoint(112.6, -48, 81),
            OrientedPoint(113.8, -38.6, 88),
            OrientedPoint(113.5, -32, 98),
            OrientedPoint(111, -24.1, 115.6),
            OrientedPoint(108.8, -21.4, 142),
            OrientedPoint(106, -20, 164),
            OrientedPoint(102.7, -19.6, 180),
            OrientedPoint(97.2, -21, -153.7),
            OrientedPoint(91.5, -24.8, -139),
            OrientedPoint(84, -33, -127.85),
            OrientedPoint(78.2, -41.2, -122.1),
            OrientedPoint(67.5, -60.6, -117),
            OrientedPoint(57, -84.8, -110.5),
            OrientedPoint(47.8, -113, -104.85),
            OrientedPoint(42, -137.5, -100.81),
            OrientedPoint(38.7, -156, -97.7),
            OrientedPoint(37, -172.6, -94.1),
            OrientedPoint(36.2, -189.2, -91.7),
            OrientedPoint(36.2, -199, -88.9),
            OrientedPoint(37.8, -217.6, -80.9),
            OrientedPoint(38.6, -221.9, -78.15),
            OrientedPoint(40.4, -228, -66.22),
            OrientedPoint(42.8, -231.9, -50.40),
            OrientedPoint(45.3, -234, -33.24),
            OrientedPoint(48.7, -235, -1.52),
            OrientedPoint(52.8, -234.3, 18),
            OrientedPoint(58, -231.2, 37.66),
            OrientedPoint(64, -225.4, 48.75),
            OrientedPoint(70, -217.8, 55),
            OrientedPoint(77, -207.8, 58.4),
            OrientedPoint(88, -189.5, 57.9),
        ]
    ]
    ex_long_spline(spline_sequence, thickness)

    thickness = 13
    spline_sequence = [
        [
            OrientedPoint(100.0000, -2230.0000, 19.0000),
            OrientedPoint(365.0000, -2055.0000, 43.0000),
            OrientedPoint(558.0000, -1810.0000, 57.2800),
            OrientedPoint(685.0000, -1600.0000, 61.0900),
            OrientedPoint(806.0000, -1365.0000, 64.0000),
            OrientedPoint(940.0000, -1078.0000, 66.3000),
            OrientedPoint(1030.0000, -850.0000, 71.0000),
            OrientedPoint(1096.0000, -630.0000, 77.0000),
            OrientedPoint(1126.0000, -480.0000, 81.0000),
            OrientedPoint(1138.0000, -386.0000, 88.0000),
            OrientedPoint(1135.0000, -320.0000, 98.0000),
            OrientedPoint(1110.0000, -241.0000, 115.6000),
            OrientedPoint(1088.0000, -214.0000, 142.0000),
            OrientedPoint(1060.0000, -200.0000, 164.0000),
            OrientedPoint(1027.0000, -196.0000, 180.0000),
            OrientedPoint(972.0000, -210.0000, -153.7000),
            OrientedPoint(915.0000, -248.0000, -139.0000),
            OrientedPoint(840.0000, -330.0000, -127.8500),
            OrientedPoint(782.0000, -412.0000, -122.1000),
            OrientedPoint(675.0000, -606.0000, -117.0000),
            OrientedPoint(570.0000, -848.0000, -110.5000),
            OrientedPoint(478.0000, -1130.0000, -104.8500),
            OrientedPoint(420.0000, -1375.0000, -100.8100),
            OrientedPoint(387.0000, -1560.0000, -97.7000),
            OrientedPoint(370.0000, -1726.0000, -94.1000),
            OrientedPoint(362.0000, -1892.0000, -91.7000),
            OrientedPoint(362.0000, -1990.0000, -88.9000),
            OrientedPoint(378.0000, -2176.0000, -80.9000),
            OrientedPoint(386.0000, -2219.0000, -78.1500),
            OrientedPoint(404.0000, -2280.0000, -66.2200),
            OrientedPoint(428.0000, -2319.0000, -50.4000),
            OrientedPoint(453.0000, -2340.0000, -33.2400),
            OrientedPoint(487.0000, -2350.0000, -1.5200),
            OrientedPoint(528.0000, -2343.0000, 18.0000),
            OrientedPoint(580.0000, -2312.0000, 37.6600),
            OrientedPoint(640.0000, -2254.0000, 48.7500),
            OrientedPoint(700.0000, -2178.0000, 55.0000),
            OrientedPoint(770.0000, -2078.0000, 58.4000),
            OrientedPoint(880.0000, -1895.0000, 57.9000),
        ]
    ]
    ex_long_spline(spline_sequence, thickness)


def run_spliner_examples(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_spliner_examples")
    logg.debug(f"Starting run_spliner_examples")

    # ex_fit_cubic_curve()
    # ex_compute_cubic_segment()
    exs_thick_spline()
    # exs_long_spline()

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_spliner_examples(args)
