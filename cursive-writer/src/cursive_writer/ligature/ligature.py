import argparse
import logging
import numpy as np
import math

# from random import seed as rseed
from timeit import default_timer as timer
import matplotlib.pyplot as plt

from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.spliner.spliner import translate_points_to_origin
from cursive_writer.spliner.spliner import sample_segment_points
from cursive_writer.spliner.spliner import fit_cubic
from cursive_writer.spliner.spliner import rototranslate_points
from cursive_writer.utils.geometric_utils import poly_model
from cursive_writer.utils.geometric_utils import slope2deg
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


def bisect_poly(coeff, d_coeff, y_target, tolerance=1e-6, x_low=0, x_high=1):
    """Finds a value of x so that |y-p(x)| < tolerance

    Also returns when |x_low-x_high| < tolerance

    A simple bisection is used, take care of setting x_low and x_high
    properly in order to find the value that you vaguely expect.
    I'm too lazy to use the derivative to find a better midpoint.

    A lot of assumptions are made on the shape of p(x), mainly on the sign of
    its second derivative, that should not change if you expect good results.

    Ties when y_target is higher/lower than y_mid are broken using the first derivative
    """
    logg = logging.getLogger(f"c.{__name__}.bisect_poly")
    logg.setLevel("INFO")
    logg.debug(f"Start bisect_poly")

    # deal with bad inputs
    if x_high < x_low:
        x_low, x_high = x_high, x_low

    while not math.isclose(x_low, x_high, abs_tol=tolerance):
        # find the midpoint
        x_mid = (x_low + x_high) / 2

        # compute the value of the function in low, mid, high
        y_low = poly_model(np.array([x_low]), coeff, flip_coeff=True)
        y_mid = poly_model(np.array([x_mid]), coeff, flip_coeff=True)
        y_high = poly_model(np.array([x_high]), coeff, flip_coeff=True)

        logg.debug(f"x_low: {x_low} x_mid: {x_mid} x_high: {x_high}")
        logg.debug(f"y_low: {y_low} y_mid: {y_mid} y_high: {y_high}")

        # if the midpoint is a good approx, return that
        if math.isclose(y_target, y_mid, abs_tol=tolerance):
            logg.debug(f"the y_target {y_target} is close to y_mid {y_mid}")
            return x_mid

        # the y_target is between y_low and y_mid
        elif y_low <= y_target <= y_mid or y_low >= y_target >= y_mid:
            logg.debug(f"the y_target {y_target} is between y_low and y_mid")
            x_high = x_mid

        # the y_target is between y_mid and y_high
        elif y_mid <= y_target <= y_high or y_mid >= y_target >= y_high:
            logg.debug(f"the y_target {y_target} is between y_mid and y_high")
            x_low = x_mid

        # the y_target is higher than y_mid (but not lower than y_high or y_low
        # else it would be in the other cases)
        elif y_target >= y_mid:
            logg.debug(f"the y_target {y_target} is over y_mid")
            y_d_mid = poly_model(np.array([x_mid]), d_coeff, flip_coeff=True)

            # the curve is going up at midpoint, pick right interval
            if y_d_mid >= 0:
                logg.debug(f"the curve is going up at midpoint, pick right interval")
                x_low = x_mid

            # the curve is going down at midpoint, pick left interval
            elif y_d_mid < 0:
                logg.debug(f"the curve is going down at midpoint, pick left interval")
                x_high = x_mid

        elif y_target <= y_mid:
            logg.debug(f"the y_target {y_target} is below y_mid")
            y_d_mid = poly_model(np.array([x_mid]), d_coeff, flip_coeff=True)

            # the curve is going up at midpoint, pick left interval
            if y_d_mid >= 0:
                logg.debug(f"the curve is going up at midpoint, pick left interval")
                x_high = x_mid

            # the curve is going down at midpoint, pick right interval
            elif y_d_mid < 0:
                logg.debug(f"the curve is going down at midpoint, pick right interval")
                x_low = x_mid

    # TODO before returning need to check if the y_mid is actually near
    # y_target, or if y_target was outside the interval requested
    return (x_low + x_high) / 2


def rotate_coeff(coeff, theta_deg):
    """Returns the parametric expression of the rotated coeff

    Given a cubic curve

        y = a*x^3 + b*x^2 + c*x + d

    It can be parametrized as
        
        [x] = [         t               ]
        [y] = [ a*t^3 + b*t^2 + c*t + d ]

    Apply a rotation of th radians
        
        [x'] = [cos(th) -sin(th)] * [         t               ]
        [y'] = [sin(th)  cos(th)]   [ a*t^3 + b*t^2 + c*t + d ]
    """
    logg = logging.getLogger(f"c.{__name__}.rotate_coeff")
    logg.debug(f"Starting rotate_coeff")

    theta_rad = math.radians(theta_deg)
    ct = math.cos(theta_rad)
    st = math.sin(theta_rad)

    a, b, c, d = coeff

    x_rot_coeff = [
        -st * a,
        -st * b,
        ct - st * c,
        -st * d,
    ]
    y_rot_coeff = [
        ct * a,
        ct * b,
        st + ct * c,
        ct * d,
    ]

    return x_rot_coeff, y_rot_coeff


def rotate_derive_coeff(coeff, theta_deg):
    """Returns the parametric expression of the derivative of the rotated coeff

    Given a cubic curve

        y = a*x^3 + b*x^2 + c*x + d

    It can be parametrized as
        
        [x] = [         t               ]
        [y] = [ a*t^3 + b*t^2 + c*t + d ]

    Apply a rotation of th radians
        
        [x'] = [cos(th) -sin(th)] * [         t               ]
        [y'] = [sin(th)  cos(th)]   [ a*t^3 + b*t^2 + c*t + d ]

    The derivative as function of t is
        
        dy   dy/dt
        -- = -----
        dx   dx/dt
    """
    theta_rad = math.radians(theta_deg)
    ct = math.cos(theta_rad)
    st = math.sin(theta_rad)

    a, b, c, d = coeff

    x_rot_d_coeff = [
        3 * -st * a,
        2 * -st * b,
        ct - st * c,
    ]
    y_rot_d_coeff = [
        3 * ct * a,
        2 * ct * b,
        st + ct * c,
    ]

    return x_rot_d_coeff, y_rot_d_coeff


def print_coeff(coeff):
    """TODO: what is print_coeff doing?
    """
    logg = logging.getLogger(f"c.{__name__}.print_coeff")
    logg.debug(f"Start print_coeff {coeff}")

    eq_str = "y ="
    for i, c in enumerate(np.flip(coeff)):
        eq_str += f" + {c} * x^{i}"

    return eq_str


def sample_parametric_aligned(
    x_coeff, y_coeff, x_d_coeff, y_d_coeff, x_min, x_max, stride
):
    """TODO: what is sample_parametric_aligned doing?

    Given a parametric curve and an interval [x_min, x_max]

        [x] = [f(t)]
        [y] = [g(t)]

    Returns an interpolation of that curve, aligned on multiples of stride.

    Let x_min = 1.7, x_max = 4.5 and stride = 0.5, the curve will be sampled in

        x_sample = [2, 2.5, 3, 3.5, 4, 4.5]

    Note that the extremes are included on both sides.
    """
    logg = logging.getLogger(f"c.{__name__}.sample_parametric_aligned")
    logg.debug(f"\nStart sample_parametric_aligned")
    logg.debug(f"x_min: {x_min} x_max: {x_max}")

    # find the value for t that corresponds to x_min and x_max
    t_min = bisect_poly(x_coeff, x_d_coeff, x_min, x_low=2 * x_min, x_high=2 * x_max)
    t_max = bisect_poly(x_coeff, x_d_coeff, x_max, x_low=2 * x_min, x_high=2 * x_max)
    logg.debug(f"t_min: {t_min} t_max: {t_max}")

    # check where the extremes are
    x_test_min = poly_model(np.array([t_min]), x_coeff, flip_coeff=True)
    y_test_min = poly_model(np.array([t_min]), y_coeff, flip_coeff=True)
    x_test_max = poly_model(np.array([t_max]), x_coeff, flip_coeff=True)
    y_test_max = poly_model(np.array([t_max]), y_coeff, flip_coeff=True)
    logg.debug(f"x_test_min: {x_test_min} x_test_max: {x_test_max}")
    # return [x_test_min, x_test_max], [y_test_min, y_test_max]

    # oversample in t
    t_oversample = np.linspace(t_min, t_max, num=10*(x_max-x_min))
    x_oversample = poly_model(t_oversample, x_coeff, flip_coeff=True)
    y_oversample = poly_model(t_oversample, y_coeff, flip_coeff=True)   
    return x_oversample, y_oversample

    # find the closest x in the aligned grid and save the value there


def build_ligature(l_p0, l_p1, r_p0, r_p1, ax):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.build_ligature")
    logg.debug(f"Starting build_ligature")

    plot_utils.add_vector(l_p0, ax, color="r", vec_len=3)
    plot_utils.add_vector(l_p1, ax, color="r", vec_len=3)
    # plot_utils.add_vector(r_p0, ax, color="r", vec_len=3)
    # plot_utils.add_vector(r_p1, ax, color="r", vec_len=3)

    # find where the points are if translated, but not rotated, to the origin
    l_tran_p0 = OrientedPoint(0, 0, l_p0.ori_deg)
    l_tran_p1 = OrientedPoint(l_p1.x - l_p0.x, l_p1.y - l_p0.y, l_p1.ori_deg)
    plot_utils.add_vector(l_tran_p0, ax, color="r", vec_len=3)
    plot_utils.add_vector(l_tran_p1, ax, color="r", vec_len=3)

    # translate the points to the origin
    l_rot_p0, l_rot_p1, l_dir_01 = translate_points_to_origin(l_p0, l_p1)
    r_rot_p0, r_rot_p1, r_dir_01 = translate_points_to_origin(r_p0, r_p1)

    # fit the cubic on the translated points
    l_coeff = fit_cubic(l_rot_p0, l_rot_p1)
    r_coeff = fit_cubic(r_rot_p0, r_rot_p1)

    # find the parametric coeff of the cubic rotated back
    l_x_rot_coeff, l_y_rot_coeff = rotate_coeff(l_coeff, l_dir_01)
    r_x_rot_coeff, r_y_rot_coeff = rotate_coeff(r_coeff, r_dir_01)
    logg.debug(f"l_x_rot_coeff: {print_coeff(l_x_rot_coeff)}")
    logg.debug(f"l_y_rot_coeff: {print_coeff(l_y_rot_coeff)}")

    # sample the cubic using the parametric coeff
    t_sample = np.linspace(-10, 30, num=50)
    l_x_sample = poly_model(t_sample, l_x_rot_coeff, flip_coeff=True)
    l_y_sample = poly_model(t_sample, l_y_rot_coeff, flip_coeff=True)
    r_x_sample = poly_model(t_sample, r_x_rot_coeff, flip_coeff=True)
    r_y_sample = poly_model(t_sample, r_y_rot_coeff, flip_coeff=True)
    ax.plot(l_x_sample, l_y_sample, color="b", ls="-", marker="")

    # translate it to the original position
    l_x_sample += l_p0.x
    l_y_sample += l_p0.y
    r_x_sample += r_p0.x
    r_y_sample += r_p0.y
    # ax.plot(l_x_sample, l_y_sample, color="g", ls="", marker=".")
    # ax.plot(r_x_sample, r_y_sample, color="g", ls="-", marker="")

    # find the parametric coeff derivative of the rotated back segments
    l_x_rot_d_coeff, l_y_rot_d_coeff = rotate_derive_coeff(l_coeff, l_dir_01)
    r_x_rot_d_coeff, r_y_rot_d_coeff = rotate_derive_coeff(r_coeff, r_dir_01)

    # sample the derived parametric expression
    l_x_d_sample = poly_model(t_sample, l_x_rot_d_coeff, flip_coeff=True)
    l_y_d_sample = poly_model(t_sample, l_y_rot_d_coeff, flip_coeff=True)
    r_x_d_sample = poly_model(t_sample, r_x_rot_d_coeff, flip_coeff=True)
    r_y_d_sample = poly_model(t_sample, r_y_rot_d_coeff, flip_coeff=True)
    # compute the value of the derivative
    l_yp_sample = np.divide(l_y_d_sample, l_x_d_sample)
    r_yp_sample = np.divide(r_y_d_sample, r_x_d_sample)

    xid = 24
    recap = f"At point l_x_sample[{xid}] {l_x_sample[xid]}"
    recap += f" l_y_sample[{xid}] {l_y_sample[xid]}"
    recap += f" l_yp_sample[{xid}] {l_yp_sample[xid]}"
    logg.debug(recap)

    # plot an example of tangent line
    tang_op = OrientedPoint(
        l_x_sample[xid], l_y_sample[xid], slope2deg(l_yp_sample[xid])
    )
    tang_coeff = tang_op.to_ab_line()
    x_sample = np.linspace(l_p0.x, l_p1.x, num=50)
    tang_y_sample = poly_model(x_sample, tang_coeff, flip_coeff=True)
    ax.plot(x_sample, tang_y_sample, color="g", ls="-", marker="")

    # sample properly the cubic in the interval
    stride = 0.1
    l_x_sample, l_y_sample = sample_parametric_aligned(
        l_x_rot_coeff,
        l_y_rot_coeff,
        l_x_rot_d_coeff,
        l_y_rot_d_coeff,
        0,
        l_p1.x - l_p0.x,
        stride,
    )
    ax.plot(l_x_sample, l_y_sample, color="r", ls="", marker=".")

    # translate it to the original position
    l_x_sample += l_p0.x
    l_y_sample += l_p0.y
    r_x_sample += r_p0.x
    r_y_sample += r_p0.y
    ax.plot(l_x_sample, l_y_sample, color="r", ls="", marker=".")

    # sample the points near the origin
    l_x_sample, l_y_segment = sample_segment_points(l_rot_p0.x, l_rot_p1.x, l_coeff)
    r_x_sample, r_y_segment = sample_segment_points(r_rot_p0.x, r_rot_p1.x, r_coeff)
    # ax.plot(l_x_sample, l_y_segment, color="g", ls="-", marker="")
    # ax.plot(r_x_sample, r_y_segment, color="y", ls="-", marker="")
    ax.plot(l_x_sample, l_y_segment, color="b", ls="", marker=".")
    # ax.plot(l_x_sample, l_y_segment, color="y", ls="", marker=".")

    # translate them back to original position
    l_x_rototran, l_y_rototran = rototranslate_points(
        l_x_sample, l_y_segment, -l_dir_01, l_p0.x, l_p0.y,
    )
    r_x_rototran, r_y_rototran = rototranslate_points(
        r_x_sample, r_y_segment, -r_dir_01, r_p0.x, r_p0.y,
    )
    # ax.plot(l_x_rototran, l_y_rototran, color="g", ls="-", marker="")
    # ax.plot(r_x_rototran, r_y_rototran, color="y", ls="-", marker="")
    # ax.plot(l_x_rototran, l_y_rototran, color="b", ls="", marker=".")
    # ax.plot(l_x_rototran, l_y_rototran, color="y", ls="", marker=".")


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
