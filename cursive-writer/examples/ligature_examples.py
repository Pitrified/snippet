import argparse
import logging
import math
import matplotlib.pyplot as plt
import numpy as np

from random import seed as rseed
from timeit import default_timer as timer

from cursive_writer.utils.utils import print_coeff
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils import plot_utils
from cursive_writer.spliner.spliner import translate_points_to_origin
from cursive_writer.spliner.spliner import fit_cubic
from cursive_writer.utils.geometric_utils import rotate_coeff
from cursive_writer.utils.geometric_utils import rotate_derive_coeff
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils.geometric_utils import sample_parametric_aligned
from cursive_writer.utils.geometric_utils import slope2deg


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


def ex_parametric_tangent(p0, p1, x_stride, ax):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.ex_parametric_tangent")
    logg.debug(f"Starting ex_parametric_tangent")

    vec_len = max(p1.x, p1.y) / 10

    # plot original points
    plot_utils.add_vector(p0, ax, color="r", vec_len=vec_len)
    plot_utils.add_vector(p1, ax, color="r", vec_len=vec_len)

    # find where the points are if translated, but not rotated, to the origin
    tran_p0 = OrientedPoint(0, 0, p0.ori_deg)
    tran_p1 = OrientedPoint(p1.x - p0.x, p1.y - p0.y, p1.ori_deg)
    plot_utils.add_vector(tran_p0, ax, color="r", vec_len=vec_len)
    plot_utils.add_vector(tran_p1, ax, color="r", vec_len=vec_len)

    # translate the points to the origin
    rot_p0, rot_p1, dir_01 = translate_points_to_origin(p0, p1)

    # fit the cubic on the translated points
    coeff = fit_cubic(rot_p0, rot_p1)

    # find the parametric coeff of the cubic rotated back
    x_rot_coeff, y_rot_coeff = rotate_coeff(coeff, dir_01)
    logg.debug(f"x_rot_coeff: {print_coeff(x_rot_coeff)}")
    logg.debug(f"y_rot_coeff: {print_coeff(y_rot_coeff)}")

    # over sample the rotated cubic using the parametric coeff
    t_o_sample = np.linspace(-10, 30, num=50)
    x_o_sample = poly_model(t_o_sample, x_rot_coeff, flip_coeff=True)
    y_o_sample = poly_model(t_o_sample, y_rot_coeff, flip_coeff=True)
    ax.plot(x_o_sample, y_o_sample, color="b", ls="-", marker="")

    # find the parametric coeff derivative of the rotated back segments
    x_rot_d_coeff, y_rot_d_coeff = rotate_derive_coeff(coeff, dir_01)

    # sample properly the cubic in the interval
    x_offset = math.ceil(p0.x / x_stride) * x_stride - p0.x

    (
        t_a_sample,
        x_a_sample,
        y_a_sample,
        x_a_d_sample,
        y_a_d_sample,
    ) = sample_parametric_aligned(
        x_rot_coeff,
        y_rot_coeff,
        x_rot_d_coeff,
        y_rot_d_coeff,
        0,
        p1.x - p0.x,
        x_stride,
        x_offset,
    )
    ax.plot(x_a_sample, y_a_sample, color="k", ls="", marker=".")
    # ax.plot(x_a_sample, y_a_sample, color="k", ls="-", marker="")

    # translate the sample to the original position
    x_a_sample += p0.x
    y_a_sample += p0.y
    # ax.plot(x_a_sample, y_a_sample, color="k", ls="", marker=".")
    ax.plot(x_a_sample, y_a_sample, color="k", ls="-", marker="")

    # compute the value of the derivative
    yp_sample = np.divide(y_a_d_sample, x_a_d_sample)

    # xid = 24
    xid = math.floor(x_a_sample.shape[0] / 2)
    recap = f"At point x_a_sample[{xid}] {x_a_sample[xid]}"
    recap += f" y_a_sample[{xid}] {y_a_sample[xid]}"
    recap += f" yp_sample[{xid}] {yp_sample[xid]}"
    logg.debug(recap)

    # plot an example of tangent line
    tang_op = OrientedPoint(x_a_sample[xid], y_a_sample[xid], slope2deg(yp_sample[xid]))
    tang_coeff = tang_op.to_ab_line()
    tang_y_a_sample = poly_model(x_a_sample, tang_coeff, flip_coeff=True)
    ax.plot(x_a_sample, tang_y_a_sample, color="g", ls="-", marker="")


def exs_parametric_tangent(args):
    """TODO: what is exs_parametric_tangent doing?
    """
    logg = logging.getLogger(f"c.{__name__}.exs_parametric_tangent")
    logg.debug(f"Start exs_parametric_tangent")

    # x_stride = 3
    x_stride = 0.3

    # create the plot
    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    p0 = OrientedPoint(10, 10, -30)
    p1 = OrientedPoint(30, 20, 70)
    ax[0][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][0])

    p0 = OrientedPoint(10, 13, -30)
    p1 = OrientedPoint(30, 20, 50)
    ax[0][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][1])

    p0 = OrientedPoint(10, 10, -10)
    p1 = OrientedPoint(30, 20, 70)
    ax[1][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][0])

    p0 = OrientedPoint(10, 10, -10)
    p1 = OrientedPoint(30, 20, 50)
    ax[1][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][1])

    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    p0 = OrientedPoint(100, 100, -30)
    p1 = OrientedPoint(300, 200, 70)
    ax[0][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][0])

    p0 = OrientedPoint(100, 130, -30)
    p1 = OrientedPoint(300, 200, 50)
    ax[0][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[0][1])

    p0 = OrientedPoint(100, 100, -10)
    p1 = OrientedPoint(300, 200, 70)
    ax[1][0].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][0])

    p0 = OrientedPoint(100, 100, -10)
    p1 = OrientedPoint(300, 200, 50)
    ax[1][1].set_title(f"{p0.ori_deg} {p1.ori_deg}")
    ex_parametric_tangent(p0, p1, x_stride, ax[1][1])


def run_ligature_examples(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_ligature_examples")
    logg.debug(f"Starting run_ligature_examples")

    exs_parametric_tangent(args)

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_ligature_examples(args)
