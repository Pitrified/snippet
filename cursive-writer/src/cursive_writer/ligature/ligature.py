import argparse
import logging
import numpy as np
import math

from timeit import default_timer as timer
import matplotlib.pyplot as plt

from cursive_writer.spliner.spliner import compute_aligned_cubic_segment
from cursive_writer.spliner.spliner import fit_cubic
from cursive_writer.spliner.spliner import rototranslate_points
from cursive_writer.spliner.spliner import sample_nat_segment_points
from cursive_writer.spliner.spliner import translate_points_to_origin
from cursive_writer.utils import plot_utils
from cursive_writer.utils.geometric_utils import bisect_poly
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils.geometric_utils import rotate_coeff
from cursive_writer.utils.geometric_utils import rotate_derive_coeff
from cursive_writer.utils.geometric_utils import sample_parametric_aligned
from cursive_writer.utils.geometric_utils import slope2deg
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.utils import print_coeff


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
    log_format_module = "%(name)s: %(message)s"
    #  log_format_module = "%(message)s"

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

    recap = f"python3 single_spline2image.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def build_ligature(l_p0, l_p1, r_p0, r_p1, ax):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.build_ligature")
    logg.debug(f"\nStarting build_ligature")
    logg.debug(f"l_p0.x: {l_p0.x} l_p1.x: {l_p1.x} r_p0.x: {r_p0.x} r_p1.x: {r_p1.x}")

    ligature_start = timer()

    # x_stride = 0.01
    # x_stride = 0.1
    # x_stride = 1
    # x_stride = 0.5
    # x_stride = 2
    # x_stride = 4
    x_stride = max(l_p1.x - l_p0.x, r_p1.x - r_p0.x) / 100
    x_stride = 10 ** math.floor(math.log(x_stride, 10))
    logg.debug(f"x_stride: {x_stride}")

    segment_start = timer()
    l_t_as, l_x_as, l_y_as, l_yp_as = compute_aligned_cubic_segment(
        l_p0, l_p1, x_stride,
    )
    r_t_as, r_x_orig_as, r_y_as, r_yp_as = compute_aligned_cubic_segment(
        r_p0, r_p1, x_stride,
    )
    segment_end = timer()
    logg.debug(f"Time to compute aligned segments: {segment_end - segment_start:.6f}")
    # logg.debug(f"r_x_orig_as[0]: {r_x_orig_as[0]} r_x_orig_as[-1]: {r_x_orig_as[-1]}")

    # find how much the right segment can shift
    shift_11 = l_p1.x - r_p1.x - (l_p1.x - l_p0.x) / 2
    shift_10 = l_p1.x - r_p0.x
    # align the shift on the stride grid: now if you sum the shift to l_x_as the points are still aligned.
    shift_a_11 = math.floor(shift_11 / x_stride) * x_stride
    shift_a_10 = math.ceil(shift_10 / x_stride) * x_stride
    shift_range = np.arange(shift_a_11, shift_a_10 + x_stride / 2, x_stride)
    recap = f"shift_11: {shift_11} shift_10: {shift_10}"
    recap += f" shift_a_11: {shift_a_11} shift_a_10: {shift_a_10}"
    # logg.debug(recap)
    # logg.debug(f"shift_range: {shift_range}")

    best_dist_x_touch = float("inf")
    best_shift = None
    best_r_x_as = None
    best_tang_y_as = None

    # plot the segments
    ax.plot(l_x_as, l_y_as, color="g", ls="-", marker="")
    # ax.plot(l_x_as, l_y_as, color="g", ls="", marker=".")

    tangent_times = []

    for shift in shift_range:
        r_x_as = r_x_orig_as + shift
        # logg.debug(f"\nNew shift r_x_as[0]: {r_x_as[0]} r_x_as[-1]: {r_x_as[-1]}")

        # ax.plot(r_x_as, r_y_as, color="y", ls="-", marker="")
        # ax.plot(r_x_as, r_y_as, color="y", ls="", marker=".")

        tangent_start = timer()
        for xid in range(r_x_as.shape[0]):
            # point tangent to the *right* segment
            tang_op = OrientedPoint(r_x_as[xid], r_y_as[xid], slope2deg(r_yp_as[xid]))
            tang_coeff = tang_op.to_ab_line()

            # sample it on the *left* segment sample
            tang_y_as = poly_model(l_x_as, tang_coeff, flip_coeff=True)
            # ax.plot(l_x_as, tang_y_as, color="b", ls="-", marker="")
            # ax.plot(l_x_as, tang_y_as, color="b", ls="", marker=".")

            # find if the left segment has some points lower than the tangent
            lower = l_y_as < tang_y_as
            # logg.debug(f"lower: {lower} {np.sum(lower)}")
            if np.sum(lower) == 0:
                # logg.debug(f"Breaking at xid: {xid}")
                break
        tangent_end = timer()
        tangent_times.append(tangent_end - tangent_start)
        # logg.debug(f"Time to find tangent: {tangent_end - tangent_start:.6f}")

        # check this better, you might have found the tangent at the last iteration...
        if xid == r_x_as.shape[0] - 1:
            # logg.debug(f"Tangent not found")
            continue

        # find distance from left segment to tangent
        dist_lt = l_y_as - tang_y_as
        min_dist_lt = np.min(dist_lt)
        argmin_dist_lt = np.argmin(dist_lt)
        recap = f"min_dist_lt: {min_dist_lt:.6f} argmin_dist_lt: {argmin_dist_lt}"
        # logg.debug(recap)

        # find where the tangent touches the segments
        l_x_touch = l_x_as[argmin_dist_lt]
        r_x_touch = r_x_as[xid]

        if r_x_touch < l_x_touch:
            # logg.debug(f"Tangent goes the wrong way")
            continue

        # extend the points of contact
        dist_x_touch = r_x_touch - l_x_touch
        l_x_ext = l_x_touch - dist_x_touch / 2
        r_x_ext = r_x_touch + dist_x_touch / 2
        recap = f"l_x_touch: {l_x_touch:.4f} r_x_touch {r_x_touch:.4f}"
        recap += f" dist_x_touch: {dist_x_touch:.4f}"
        recap += f" l_x_ext: {l_x_ext:.4f} r_x_ext {r_x_ext:.4f}"
        # logg.debug(recap)

        if dist_x_touch < best_dist_x_touch:
            best_dist_x_touch = dist_x_touch
            best_shift = shift
            best_r_x_as = r_x_as
            best_tang_y_as = tang_y_as

        lower_x = l_x_as < l_x_ext
        # argmin returns the *first* occurrence of the min value
        argmin_lower_x = np.argmin(lower_x)
        # for symmetry, if we can, we keep the previous index (the last of the True)
        if argmin_lower_x > 0:
            argmin_lower_x -= 1
        # recap = f"lower_x: {lower_x}"
        recap = f" argmin_lower_x: {argmin_lower_x}"
        recap += f" l_x_as[argmin_lower_x]: {l_x_as[argmin_lower_x]}"
        # logg.debug(recap)

        lower_x = r_x_as < r_x_ext
        # argmin returns the *first* occurrence of the min value
        argmin_lower_x = np.argmin(lower_x)
        # recap = f"lower_x: {lower_x}"
        recap = f" argmin_lower_x: {argmin_lower_x}"
        recap += f" r_x_as[argmin_lower_x]: {r_x_as[argmin_lower_x]}"
        # logg.debug(recap)

        # plot the last tangent found
        # ax.plot(l_x_as, tang_y_as, color="b", ls="-", marker="")

    tangent_time_mean = sum(tangent_times) / len(tangent_times)
    logg.debug(f"Mean tangent time: {tangent_time_mean}")

    ligature_end = timer()
    logg.debug(f"Time for build_ligature: {ligature_end - ligature_start:.6f}")

    ax.plot(best_r_x_as, r_y_as, color="y", ls="-", marker="")
    ax.plot(l_x_as, best_tang_y_as, color="b", ls="-", marker="")


def exs_build_ligature():
    """
    """
    logg = logging.getLogger(f"c.{__name__}.exs_build_ligature")
    logg.debug(f"Starting exs_build_ligature")

    # create the plot
    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    l_p0 = OrientedPoint(10, 10, -30)
    l_p1 = OrientedPoint(30, 20, 70)
    r_p0 = OrientedPoint(15, 10, -10)
    r_p1 = OrientedPoint(32, 20, 50)
    ax[0][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[0][0])

    l_p0 = OrientedPoint(10, 13, -30)
    l_p1 = OrientedPoint(30, 20, 50)
    r_p0 = OrientedPoint(15, 12, -10)
    r_p1 = OrientedPoint(32, 20, 70)
    ax[0][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[0][1])

    l_p0 = OrientedPoint(10, 10, -10)
    l_p1 = OrientedPoint(30, 20, 70)
    r_p0 = OrientedPoint(15, 13, -30)
    r_p1 = OrientedPoint(32, 20, 50)
    ax[1][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[1][0])

    l_p0 = OrientedPoint(10, 10, -10)
    l_p1 = OrientedPoint(30, 20, 50)
    r_p0 = OrientedPoint(15, 13, -30)
    r_p1 = OrientedPoint(32, 20, 70)
    ax[1][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[1][1])

    # plt.show()
    # return

    # create the plot
    fig, ax = plt.subplots(2, 2)
    fig.set_size_inches(11, 8)
    ax[0][0].grid()
    ax[0][1].grid()
    ax[1][0].grid()
    ax[1][1].grid()

    l_p0 = OrientedPoint(100, 100, -30)
    l_p1 = OrientedPoint(300, 200, 70)
    r_p0 = OrientedPoint(150, 100, -10)
    r_p1 = OrientedPoint(320, 200, 50)
    ax[0][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[0][0])

    l_p0 = OrientedPoint(100, 130, -30)
    l_p1 = OrientedPoint(300, 200, 50)
    r_p0 = OrientedPoint(150, 120, -10)
    r_p1 = OrientedPoint(320, 200, 70)
    ax[0][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[0][1])

    l_p0 = OrientedPoint(100, 100, -10)
    l_p1 = OrientedPoint(300, 200, 70)
    r_p0 = OrientedPoint(150, 130, -30)
    r_p1 = OrientedPoint(320, 200, 50)
    ax[1][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[1][0])

    l_p0 = OrientedPoint(100, 100, -10)
    l_p1 = OrientedPoint(300, 200, 50)
    r_p0 = OrientedPoint(150, 130, -30)
    r_p1 = OrientedPoint(320, 200, 70)
    ax[1][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    build_ligature(l_p0, l_p1, r_p0, r_p1, ax[1][1])

    plt.show()


def run_ligature(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_ligature")
    logg.debug(f"Starting run_ligature")

    exs_build_ligature()


if __name__ == "__main__":
    args = setup_env()
    run_ligature(args)
