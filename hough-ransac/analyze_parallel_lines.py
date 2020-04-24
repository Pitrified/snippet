import argparse
import logging
import math
import numpy as np
import matplotlib.pyplot as plt

from random import seed as rseed
from timeit import default_timer as timer

from analyze_laser_data import load_filer_data
from hough_parallel import HoughParallel


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
    data_file_name = "laser_data_straight.txt"

    left_filt_x, left_filt_y, right_filt_x, right_filt_y = load_filer_data(
        data_file_name, sector_wid
    )

    data_x = np.hstack((left_filt_x, right_filt_x))
    data_y = np.hstack((left_filt_y, right_filt_y))
    # data_y -= 1
    logg.debug(f"Loaded data_x.shape: {data_x.shape} data_y.shape {data_y.shape}")

    # create the HoughParallel analyzer
    hp = HoughParallel(
        data_x, data_y, corridor_width, r_stride, r_min_dist, r_max_dist, th_bin_num
    )

    t_analyze_start = timer()
    # find the corridor
    # best_th, best_r = hp.find_parallel_lines()
    best_th, best_r = hp.find_parallel_lines_mat()
    logg.debug(f"best_th: {best_th} best_r {best_r} pi-best_th {math.pi-best_th}")

    t_analyze_end = timer()
    logg.debug(f"Analyzing took {t_analyze_end-t_analyze_start} seconds")

    #############################################
    # standard fitting of two independent lines #
    #############################################

    left_coeff = np.polyfit(left_filt_x, left_filt_y, 1)
    right_coeff = np.polyfit(right_filt_x, right_filt_y, 1)
    logg.debug(f"left_coeff: {left_coeff} right_coeff {right_coeff}")
    # setup plot
    fig, ax = plt.subplots(1, 3)
    fig.set_size_inches((24, 8))
    ax_points = ax[0]
    # plot the laser dataset
    style_points_all = {"ls": "", "marker": ".", "color": "k"}
    ax_points.plot(left_filt_x, left_filt_y, **style_points_all)
    ax_points.plot(right_filt_x, right_filt_y, **style_points_all)
    # plot the left fit line
    left_fit_y = np.polyval(left_coeff, left_filt_x)
    style_fit = {"ls": "-", "marker": "", "color": "b"}
    ax_points.plot(left_filt_x, left_fit_y, **style_fit)
    # plot the right fit line
    right_fit_y = np.polyval(right_coeff, right_filt_x)
    style_fit = {"ls": "-", "marker": "", "color": "b"}
    ax_points.plot(right_filt_x, right_fit_y, **style_fit)

    hp.visual_test_all_dist_all_th(ax[1])
    hp.visual_test_bins(ax[2])

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_analyze_parallel_lines(args)
