import argparse
import logging
import math
import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from random import seed as rseed
from timeit import default_timer as timer
from pathlib import Path

from analyze_laser_data import load_filer_data
from hough_parallel import HoughParallel
# from double_hough import DoubleHough
from double_hough import VisualDoubleHough
from utils import slope2deg
from utils import slope2rad


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

    # log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    # log_format_module = "%(name)s - %(levelname)s: %(message)s"
    # log_format_module = '%(levelname)s: %(message)s'
    # log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


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
    recap = f"python3 analyze_parallel_lines.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def visual_test_shift(hp):
    """TODO: what is visual_test_shift doing?
    """
    logg = logging.getLogger(f"c.{__name__}.visual_test_shift")
    logg.debug(f"Start visual_test_shift")

    # plot all the shift values
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches((8, 8))
    ax.set_title("Shift test")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    style = {"ls": "", "marker": ".", "color": "k"}
    ax.plot(hp.shift_val_x, hp.shift_val_y, **style)


def visual_test_dist_all_th(hp, dist_all_th_left, dist_all_th_right):
    """TODO: what is visual_test_dist_all_th doing?
    """
    logg = logging.getLogger(f"c.{__name__}.visual_test_dist_all_th")
    logg.debug(f"Start visual_test_dist_all_th")

    # plot all the shift values
    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches((8, 8))
    ax.set_title("Test dist_all_th")
    ax.set_xlabel("theta")
    ax.set_ylabel("r")

    style = {"ls": "", "marker": ".", "color": "k"}
    ax.plot(hp.th_values, dist_all_th_left, **style)
    ax.plot(hp.th_values, dist_all_th_right, **style)


def visual_test_all_dist_all_th(hp, ax=None):
    """TODO: what is visual_test_all_dist_all_th doing?
    """
    logg = logging.getLogger(f"c.{__name__}.visual_test_all_dist_all_th")
    logg.debug(f"Start visual_test_all_dist_all_th")

    if ax is None:
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches((8, 8))
        ax.set_title("Test all_dist_all_th")
        ax.set_xlabel("theta")
        ax.set_ylabel("r")

    style = {"ls": "-", "marker": "", "color": "y"}
    # style = {"ls": "", "marker": ".", "color": "y"}
    for dist_all_th in hp.all_dist_all_th_l:
        # dist_all_th /= hp.r_stride
        ax.plot(hp.th_values, dist_all_th, **style)
    style["color"] = "g"
    for dist_all_th in hp.all_dist_all_th_r:
        # dist_all_th /= hp.r_stride
        ax.plot(hp.th_values, dist_all_th, **style)

    style = {"ls": "", "marker": ".", "color": "c"}
    for dist_all_th in hp.int_all_dist_all_th:
        # ax.plot(hp.th_values, dist_all_th, **style)
        pass


def visual_test_bins(hp, ax=None):
    """TODO: what is visual_test_bins doing?

    matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches((8, 8))
        ax.set_title("Test bins")
        ax.set_xlabel("theta")
        ax.set_ylabel("r")

    im = ax.imshow(hp.bins.T)

    ax.invert_yaxis()
    ax.set_title("Lines per bin")

    cbar = 0
    # cbar_kw = {"orientation": "horizontal"}
    # cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    # cbarlabel = "Lines per bin"
    # cbar.ax.set_ylabel(cbarlabel, rotation=90, va="baseline")
    # cbar.ax.set_ylabel(cbarlabel)

    return im, cbar


def fit_separate_lines(left_filt_x, left_filt_y, right_filt_x, right_filt_y, ax_points):
    left_coeff = np.polyfit(left_filt_x, left_filt_y, 1)
    right_coeff = np.polyfit(right_filt_x, right_filt_y, 1)

    # plot the laser dataset
    style_points_all = {"ls": "", "marker": ".", "color": "k"}
    ax_points.plot(left_filt_x, left_filt_y, **style_points_all)
    ax_points.plot(right_filt_x, right_filt_y, **style_points_all)

    # plot the left fit line
    left_fit_y = np.polyval(left_coeff, left_filt_x)
    style_fit = {"ls": "-", "marker": "", "color": "b"}
    ax_points.plot(left_filt_x, left_fit_y, label="Left line", **style_fit)

    # plot the right fit line
    right_fit_y = np.polyval(right_coeff, right_filt_x)
    style_fit["color"] = "g"
    ax_points.plot(right_filt_x, right_fit_y, label="Right line", **style_fit)

    # some info on the result
    logg = logging.getLogger(f"c.{__name__}.fit_separate_lines")
    logg.debug(f"left_coeff: {left_coeff} right_coeff {right_coeff}")
    left_deg = slope2deg(left_coeff[0])
    right_deg = slope2deg(right_coeff[0])
    logg.debug(f"left_deg: {left_deg} right_deg {right_deg}")
    left_rad = slope2rad(left_coeff[0])
    right_rad = slope2rad(right_coeff[0])
    logg.debug(f"left_rad: {left_rad} right_rad {right_rad}")


def rth2ab(r, norm_th):
    """Given the distance from the origin and the normal direction theta, compute the
    coefficient of the line
    """
    # logg = logging.getLogger(f"c.{__name__}.rth2ab")
    # logg.debug(f"Start rth2ab")

    # point on the line
    x = math.cos(norm_th) * r
    y = math.sin(norm_th) * r

    # direction of the line
    th = norm_th + math.pi / 2

    # coefficients
    a = math.tan(th)
    b = y - a * x
    return np.array([a, b])


def run_compare(args):
    """TODO: what is run_compare doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_compare")
    logg.debug(f"Start run_compare")

    ########################
    # set hough parameters #
    ########################

    # set sector_wid in degrees
    # sector_wid_deg = 30
    sector_wid_deg = 60
    sector_wid = math.floor(sector_wid_deg / 180 * 200)
    logg.debug(f"sector_wid: {sector_wid} degrees {sector_wid_deg}")

    # r dimension of the bins
    # r_stride = 0.05
    # r_stride = 0.01
    r_stride = 0.005
    # r_stride = 0.0025
    r_min_dist = 0.1
    r_max_dist = 0.6

    # number of bins in the [0, 180) interval
    # th_bin_num = 12
    # th_bin_num = 36
    # th_bin_num = 180
    th_bin_num = 360
    # th_bin_num = 720

    # the corridor width
    corridor_width = 0.56

    # create the HoughParallel analyzer
    hp = HoughParallel(
        0, 0, corridor_width, r_stride, r_min_dist, r_max_dist, th_bin_num
    )

    separate_delta = []
    separate_values = []
    separate_errors = []
    all_t_analyze = []
    all_t_fit = []
    parallel_values = []
    parallel_errors = []

    base_name_fmt = "ld_03_{:03d}.txt"
    main_dir = Path(__file__).resolve().parent
    for i in range(1000):
        data_file_name = base_name_fmt.format(i)
        data_file = main_dir / "laser_data" / data_file_name
        if not data_file.exists():
            break

        logg.debug(f"\ndata_file.name: {data_file.name}")

        # load the data
        left_filt_x, left_filt_y, right_filt_x, right_filt_y, data = load_filer_data(
            data_file_name, sector_wid
        )
        data_x = np.hstack((left_filt_x, right_filt_x))
        data_y = np.hstack((left_filt_y, right_filt_y))
        true_yaw = data["odom_robot_yaw"]

        hp.data_x = data_x
        hp.data_y = data_y

        # separate lines
        t_fit_start = timer()
        left_coeff = np.polyfit(left_filt_x, left_filt_y, 1)
        right_coeff = np.polyfit(right_filt_x, right_filt_y, 1)
        t_fit_end = timer()
        all_t_fit.append(t_fit_end - t_fit_start)

        # save results
        left_rad = slope2rad(left_coeff[0])
        right_rad = slope2rad(right_coeff[0])
        separate_delta.append(left_rad - right_rad)
        separate_yaw = (left_rad + right_rad) / 2
        separate_values.append(separate_yaw)
        separate_errors.append(true_yaw + separate_yaw - math.pi / 2)

        # parallel lines
        t_analyze_start = timer()
        best_th, best_r = hp.find_parallel_lines_mat()
        t_analyze_end = timer()
        all_t_analyze.append(t_analyze_end - t_analyze_start)
        left_line_coeff = rth2ab(best_r, best_th)
        left_line_rad = slope2rad(left_line_coeff[0])

        # save results
        parallel_values.append(left_line_rad)
        parallel_errors.append(true_yaw + left_line_rad - math.pi / 2)

        recap = f"true_yaw: {true_yaw:.4f}"
        recap += f" separate_yaw: {separate_yaw:.4f}"
        recap += f" parallel_yaw: {left_line_rad:.4f}"
        logg.debug(recap)

    mean_separate_value = np.mean(separate_values)
    mean_separate_errors = np.mean(np.abs(separate_errors))
    mean_separate_delta = np.mean(np.abs(separate_delta))
    mean_parallel_value = np.mean(parallel_values)
    mean_parallel_errors = np.mean(np.abs(parallel_errors))
    mean_all_t_analyze = np.mean(all_t_analyze)
    mean_all_t_fit = np.mean(all_t_fit)
    logg.debug(f"mean_separate_value:  {mean_separate_value:9.6f}")
    logg.debug(f"mean_separate_errors: {mean_separate_errors:9.6f}")
    logg.debug(f"mean_separate_delta:  {mean_separate_delta:9.6f}")
    logg.debug(f"mean_parallel_value:  {mean_parallel_value:9.6f}")
    logg.debug(f"mean_parallel_errors: {mean_parallel_errors:9.6f}")
    logg.debug(f"mean_all_t_analyze:   {mean_all_t_analyze:9.6f}")
    logg.debug(f"mean_all_t_fit:       {mean_all_t_fit:9.6f}")


def run_analyze_parallel_lines(args):
    """TODO: What is analyze_parallel_lines doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_analyze_parallel_lines")
    logg.debug(f"Starting run_analyze_parallel_lines")

    ########################
    # set hough parameters #
    ########################

    # set sector_wid in degrees
    sector_wid_deg = 30
    # sector_wid_deg = 60
    sector_wid = math.floor(sector_wid_deg / 180 * 200)
    logg.debug(f"sector_wid: {sector_wid} degrees {sector_wid_deg}")

    # r dimension of the bins
    # r_stride = 0.05
    # r_stride = 0.01
    r_stride = 0.005
    # r_stride = 0.0025
    r_min_dist = 0.1
    r_max_dist = 0.6

    # number of bins in the [0, 180) interval
    # th_bin_num = 12
    # th_bin_num = 36
    # th_bin_num = 180
    th_bin_num = 360
    # th_bin_num = 720

    # the corridor width
    corridor_width = 0.56

    #######################
    # load the laser data #
    #######################

    # data_file_name = "laser_data_16707.txt"
    # data_file_name = "ld_03_059.txt"
    data_file_name = "laser_data_straight.txt"

    left_filt_x, left_filt_y, right_filt_x, right_filt_y, data = load_filer_data(
        data_file_name, sector_wid
    )

    data_x = np.hstack((left_filt_x, right_filt_x))
    data_y = np.hstack((left_filt_y, right_filt_y))
    # shifting the data can be interesting to see how the sinusoids change shape
    # data_y -= 1
    logg.debug(f"Loaded data_x.shape: {data_x.shape} data_y.shape {data_y.shape}")

    #####################
    # find the corridor #
    #####################

    # create the HoughParallel analyzer
    hp = HoughParallel(
        data_x, data_y, corridor_width, r_stride, r_min_dist, r_max_dist, th_bin_num
    )

    t_analyze_start = timer()
    best_th, best_r = hp.find_parallel_lines_mat()
    t_analyze_end = timer()
    logg.debug(f"best_th: {best_th} best_r {best_r} pi/2-best_th {math.pi/2-best_th}")
    logg.debug(f"Analyzing took {t_analyze_end-t_analyze_start} seconds")

    # setup plot
    fig, ax = plt.subplots(1, 3)
    fig.set_size_inches((24, 8))
    ax_points = ax[0]

    # standard fitting of two independent lines
    fit_separate_lines(left_filt_x, left_filt_y, right_filt_x, right_filt_y, ax_points)

    # plot distances and heatmap
    visual_test_all_dist_all_th(hp, ax[1])
    visual_test_bins(hp, ax[2])

    # compute and plot the houghlines found
    left_line_coeff = rth2ab(best_r + corridor_width, best_th)
    right_line_coeff = rth2ab(best_r, best_th)
    left_line_y = np.polyval(left_line_coeff, left_filt_x)
    right_line_y = np.polyval(right_line_coeff, right_filt_x)
    style_hough = {"ls": "-", "marker": "", "color": "r"}
    ax_points.plot(left_filt_x, left_line_y, label="HoughParallel", **style_hough)
    ax_points.plot(right_filt_x, right_line_y, **style_hough)
    ax_points.legend(loc="center left")

    fig.tight_layout()
    plt.show()


def run_double_hough(args):
    """TODO: what is run_double_hough doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_double_hough")
    logg.debug(f"Start run_double_hough")

    ########################
    # set hough parameters #
    ########################

    # set sector_wid in degrees
    sector_wid_deg = 30
    # sector_wid_deg = 60
    sector_wid = math.floor(sector_wid_deg / 180 * 200)
    logg.debug(f"sector_wid: {sector_wid} degrees {sector_wid_deg}")

    # r dimension of the bins (cm)
    r_stride_fp = 0.025

    # number of bins in the [0, 180) interval
    th_bin_num_fp = 60

    # r dimension of the bins in the second pass (cm)
    r_stride_sp = 0.0025

    # number of bins in the precise interval in the second pass
    th_bin_num_sp = 81

    # the corridor width
    corridor_width = 0.56

    #######################
    # load the laser data #
    #######################

    # data_file_name = "laser_data_16707.txt"
    # data_file_name = "ld_03_059.txt"
    data_file_name = "laser_data_straight.txt"

    left_filt_x, left_filt_y, right_filt_x, right_filt_y, data = load_filer_data(
        data_file_name, sector_wid
    )

    data_x = np.hstack((left_filt_x, right_filt_x))
    data_y = np.hstack((left_filt_y, right_filt_y))
    # shifting the data can be interesting to see how the sinusoids change shape
    # data_y -= 1
    logg.debug(f"Loaded data_x.shape: {data_x.shape} data_y.shape {data_y.shape}")

    #####################
    # find the corridor #
    #####################

    # dh = DoubleHough(
    dh = VisualDoubleHough(
        data_x,
        data_y,
        r_stride_fp,
        th_bin_num_fp,
        r_stride_sp,
        th_bin_num_sp,
        corridor_width,
    )

    t_analyze_start = timer()
    best_th, best_r = dh.find_parallel_lines()
    t_analyze_end = timer()
    recap = f"\nbest_th: {best_th:.6f} ({math.degrees(best_th):.6f})"
    recap += f" best_r {best_r}"
    recap += f" best_th-pi/2 {best_th-math.pi/2:.6f}"
    recap += f" ({math.degrees(best_th-math.pi/2):.6f})\n"
    logg.debug(recap)
    logg.debug(f"Analyzing took {t_analyze_end-t_analyze_start} seconds")

    ################
    # plot results #
    ################

    # setup plot
    fig, ax = plt.subplots(1, 3)
    fig.set_size_inches((24, 8))
    ax_points = ax[0]

    # standard fitting of two independent lines
    fit_separate_lines(left_filt_x, left_filt_y, right_filt_x, right_filt_y, ax_points)

    # plot distances and heatmap
    dh.visual_test_all_dist_sp_th(ax[1])
    dh.visual_test_bins_sp(ax[2])

    # compute and plot the houghlines found
    left_line_coeff = rth2ab(best_r + corridor_width, best_th)
    right_line_coeff = rth2ab(best_r, best_th)
    left_line_y = np.polyval(left_line_coeff, left_filt_x)
    right_line_y = np.polyval(right_line_coeff, right_filt_x)
    style_hough = {"ls": "-", "marker": "", "color": "r"}
    ax_points.plot(left_filt_x, left_line_y, label="HoughParallel", **style_hough)
    ax_points.plot(right_filt_x, right_line_y, **style_hough)
    ax_points.legend(loc="center left")

    fig.tight_layout()
    plt.show()


def load_laser_data(data_file_name, sector_wid):
    """TODO: what is load_laser_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_laser_data")
    logg.debug(f"Start load_laser_data")

    left_filt_x, left_filt_y, right_filt_x, right_filt_y, data = load_filer_data(
        data_file_name, sector_wid
    )

    data_x = np.hstack((left_filt_x, right_filt_x))
    data_y = np.hstack((left_filt_y, right_filt_y))
    # shifting the data can be interesting to see how the sinusoids change shape
    # data_y -= 1
    logg.debug(f"Loaded data_x.shape: {data_x.shape} data_y.shape {data_y.shape}")

    return data_x, data_y


if __name__ == "__main__":
    args = setup_env()
    # run_analyze_parallel_lines(args)
    # run_compare(args)
    run_double_hough(args)
