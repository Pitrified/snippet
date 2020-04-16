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
from cursive_writer.spliner.spliner import compute_aligned_cubic_segment
from cursive_writer.utils.geometric_utils import poly_model
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
    logg.debug(f"\nStarting ex_parametric_tangent")

    t_a_sample, x_a_sample, y_a_sample, yp_a_sample = compute_aligned_cubic_segment(
        p0, p1, x_stride, ax
    )

    # xid = 24
    xid = math.floor(x_a_sample.shape[0] / 2)
    recap = f"At point x_a_sample[{xid}] {x_a_sample[xid]}"
    recap += f" y_a_sample[{xid}] {y_a_sample[xid]}"
    recap += f" yp_a_sample[{xid}] {yp_a_sample[xid]}"
    logg.debug(recap)

    # plot an example of tangent line
    tang_op = OrientedPoint(
        x_a_sample[xid], y_a_sample[xid], slope2deg(yp_a_sample[xid])
    )
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


def ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.ex_ligature_2segments")
    logg.debug(f"\nStarting ex_ligature_2segments")
    logg.debug(f"l_p0.x: {l_p0.x} l_p1.x: {l_p1.x} r_p0.x: {r_p0.x} r_p1.x: {r_p1.x}")

    ligature_start = timer()

    # find stride roughly a hundredth of the segment length
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

        # find distance from left segment to tangent
        dist_left_tangent = l_y_as - tang_y_as
        min_dist_left_tangent = np.min(dist_left_tangent)
        argmin_dist_left_tangent = np.argmin(dist_left_tangent)
        recap = f"min_dist_left_tangent: {min_dist_left_tangent:.6f}"
        recap += " argmin_dist_left_tangent: {argmin_dist_left_tangent}"
        # logg.debug(recap)

        if min_dist_left_tangent < 0:
            # logg.debug(f"Tangent not found")
            continue

        # find where the tangent touches the segments
        l_x_touch = l_x_as[argmin_dist_left_tangent]
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

        # if this shift does not improve the distance, go to the next
        if dist_x_touch >= best_dist_x_touch:
            continue

        # save info about the current shift
        best_dist_x_touch = dist_x_touch
        best_shift = shift
        best_r_x_as = r_x_as
        best_tang_y_as = tang_y_as

        # find the index of the touch points
        # left
        l_lower_x = l_x_as < l_x_ext
        # argmin returns the *first* occurrence of the min value
        l_id_e_x = np.argmin(l_lower_x)
        # for symmetry, if we can, we keep the previous index (the last of the True)
        if l_id_e_x > 0:
            l_id_e_x -= 1
        # right
        r_lower_x = r_x_as < r_x_ext
        r_id_e_x = np.argmin(r_lower_x)
        recap = f"l_id_e_x: {l_id_e_x}"
        recap += f" l_x_as[l_id_e_x]: {l_x_as[l_id_e_x]:.4f}"
        recap += f" r_id_e_x: {r_id_e_x}"
        recap += f" r_x_as[r_id_e_x]: {r_x_as[r_id_e_x]:.4f}"
        # logg.debug(recap)

    tangent_time_mean = sum(tangent_times) / len(tangent_times)
    logg.debug(f"Mean tangent time: {tangent_time_mean}")

    ligature_end = timer()
    logg.debug(f"Time to find optimal shift: {ligature_end - ligature_start:.6f}")

    # extract the best value as current
    r_x_as = best_r_x_as
    # r_x_as = r_x_orig_as + best_shift

    # find the extended contact point
    l_p_ext = OrientedPoint(
        l_x_as[l_id_e_x], l_y_as[l_id_e_x], slope2deg(l_yp_as[l_id_e_x])
    )
    r_p_ext = OrientedPoint(
        r_x_as[r_id_e_x], r_y_as[r_id_e_x], slope2deg(r_yp_as[r_id_e_x])
    )
    ext_t_as, ext_x_as, ext_y_as, ext_yp_as = compute_aligned_cubic_segment(
        l_p_ext, r_p_ext, x_stride,
    )

    recap = f"l_id_e_x: {l_id_e_x}"
    recap += f" l_x_as[l_id_e_x]: {l_x_as[l_id_e_x]:.4f}"
    recap += f" ext_x_as[0]: {ext_x_as[0]:.4f}"
    recap += f" ext_x_as[-1]: {ext_x_as[-1]:.4f}"
    recap += f" r_id_e_x: {r_id_e_x}"
    recap += f" r_x_as[r_id_e_x]: {r_x_as[r_id_e_x]:.4f}"
    logg.debug(recap)

    # show id to use when plotting
    l_id_s_x = l_id_e_x
    r_id_s_x = r_id_e_x

    # fix the ext ids, there is a gap of 1 (one) stride missing on one side
    if not math.isclose(l_x_as[l_id_e_x], ext_x_as[0]):
        logg.debug(f"Left not close")
        # check that is not the last
        if l_id_e_x < l_x_as.shape[0] - 1:
            l_id_s_x = l_id_e_x + 1

    if not math.isclose(r_x_as[r_id_e_x], ext_x_as[-1]):
        logg.debug(f"Right not close")
        # check that is not the first
        if r_id_e_x > 0:
            r_id_s_x = r_id_e_x - 1

    # plot the segments
    # ax.plot(l_x_as, l_y_as, color="g", ls="", marker=".")
    # ax.plot(r_x_as, r_y_as, color="y", ls="", marker=".")
    ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="g", ls="-")
    ax.plot(r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="y", ls="-")
    # ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="k", ls="-")
    # ax.plot(r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="k", ls="-")
    # ax.plot(l_x_as[: l_id_s_x + 1], l_y_as[: l_id_s_x + 1], color="g", marker=".")
    # ax.plot(r_x_as[r_id_s_x:], r_y_as[r_id_s_x:], color="y", marker=".")
    ax.plot(ext_x_as, ext_y_as, color="k", ls="-", marker="")

    ax.plot(l_p_ext.x, l_p_ext.y, color="r", ls="", marker="o", fillstyle="none")
    ax.plot(r_p_ext.x, r_p_ext.y, color="r", ls="", marker="o", fillstyle="none")

    ax.plot(l_x_as, best_tang_y_as, color="b", ls=":", marker="")

    vec_len = max(l_p1.x, r_p1.y) / 10
    plot_utils.add_vector(l_p_ext, ax, color="r", vec_len=vec_len)
    plot_utils.add_vector(r_p_ext, ax, color="r", vec_len=vec_len)


def exs_ligature_2segments(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.exs_build_ligature")
    logg.debug(f"Starting exs_build_ligature")

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    l_p0 = OrientedPoint(1213, 682, -12)
    l_p1 = OrientedPoint(1579, 937, 60)
    r_p0 = OrientedPoint(50, 700, -15)
    r_p1 = OrientedPoint(582, 976, 70)
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax)

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
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][0])

    l_p0 = OrientedPoint(10, 13, -30)
    l_p1 = OrientedPoint(30, 20, 50)
    r_p0 = OrientedPoint(15, 12, -10)
    r_p1 = OrientedPoint(32, 20, 70)
    ax[0][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][1])

    l_p0 = OrientedPoint(10, 10, -10)
    l_p1 = OrientedPoint(30, 20, 70)
    r_p0 = OrientedPoint(15, 13, -30)
    r_p1 = OrientedPoint(32, 20, 50)
    ax[1][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][0])

    l_p0 = OrientedPoint(10, 10, -10)
    l_p1 = OrientedPoint(30, 20, 50)
    r_p0 = OrientedPoint(15, 13, -30)
    r_p1 = OrientedPoint(32, 20, 70)
    ax[1][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][1])

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
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][0])

    l_p0 = OrientedPoint(100, 130, -30)
    l_p1 = OrientedPoint(300, 200, 50)
    r_p0 = OrientedPoint(150, 120, -10)
    r_p1 = OrientedPoint(320, 200, 70)
    ax[0][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[0][1])

    l_p0 = OrientedPoint(100, 100, -10)
    l_p1 = OrientedPoint(300, 200, 70)
    r_p0 = OrientedPoint(150, 130, -30)
    r_p1 = OrientedPoint(320, 200, 50)
    ax[1][0].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][0])

    l_p0 = OrientedPoint(100, 100, -10)
    l_p1 = OrientedPoint(300, 200, 50)
    r_p0 = OrientedPoint(150, 130, -30)
    r_p1 = OrientedPoint(320, 200, 70)
    ax[1][1].set_title(f"{l_p0.ori_deg} {l_p1.ori_deg} : {r_p0.ori_deg} {r_p1.ori_deg}")
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax[1][1])

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches(8, 8)
    l_p0 = OrientedPoint(1213, 682, -3)
    l_p1 = OrientedPoint(1579, 937, 50)
    r_p0 = OrientedPoint(50, 700, -15)
    r_p1 = OrientedPoint(582, 976, 70)
    ex_ligature_2segments(l_p0, l_p1, r_p0, r_p1, ax)

    plt.show()


def run_ligature_examples(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_ligature_examples")
    logg.debug(f"Starting run_ligature_examples")

    exs_parametric_tangent(args)
    exs_ligature_2segments(args)

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_ligature_examples(args)
