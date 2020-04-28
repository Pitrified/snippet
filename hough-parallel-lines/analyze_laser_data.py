import argparse
import logging
import math
import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from random import seed as rseed
from timeit import default_timer as timer

from utils import load_data
from utils import rth2ab
from utils import polar_to_cartesian
from utils import dist_2D


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
    recap = f"python3 analyze_laser_data.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def extract_filt_lr(sector_wid, ranges, angles_rad, range_min, range_max):
    """Extract and filter the LaserScan data
    """
    # logg = logging.getLogger(f"c.{__name__}.extract_filt_lr")
    # logg.debug(f"Start extract_filt_lr")

    # get left values
    left_center = 300
    left_slice = slice(left_center - sector_wid, left_center + sector_wid)
    left_ranges = ranges[left_slice]
    left_angles_rad = angles_rad[left_slice]

    # filter out overflow values
    left_condition = np.where(
        (range_min < left_ranges) & (left_ranges < range_max), True, False
    )
    left_ranges_filt = np.extract(left_condition, left_ranges)
    left_angles_rad_filt = np.extract(left_condition, left_angles_rad)

    left_filt_x, left_filt_y = polar_to_cartesian(
        left_ranges_filt, left_angles_rad_filt
    )
    # , odom_robot_yaw, *odom_robot_pose
    # we DO NOT rotate and translate the data, we work in the base_footprint frame to
    # have better coefficient of the line, then we will translate the model found

    # get right values
    right_center = 100
    right_slice = slice(right_center - sector_wid, right_center + sector_wid)
    right_ranges = ranges[right_slice]
    right_angles_rad = angles_rad[right_slice]

    # filter out overflow values
    right_condition = np.where(
        (range_min < right_ranges) & (right_ranges < range_max), True, False
    )
    right_ranges_filt = np.extract(right_condition, right_ranges)
    right_angles_rad_filt = np.extract(right_condition, right_angles_rad)

    right_filt_x, right_filt_y = polar_to_cartesian(
        right_ranges_filt, right_angles_rad_filt
    )

    # style = {"ls": "-", "marker": "."}
    # ax = plot_add_create(left_filt_x, left_filt_y, **style)
    # ax.set_title("Filtered left/right data")
    # plot_add_create(0, 0, ax=ax, **style)
    # plot_add_create(right_filt_x, right_filt_y, ax=ax, **style)

    return left_filt_x, left_filt_y, right_filt_x, right_filt_y


def fit_parallel_lines(left_filt_x, left_filt_y, right_filt_x, right_filt_y):
    """Fit two lines separately in the data
    """
    # logg = logging.getLogger(f"c.{__name__}.fit_parallel_lines")
    # logg.debug(f"Start fit_parallel_lines")

    left_coeff = np.polyfit(left_filt_x, left_filt_y, 1)
    right_coeff = np.polyfit(right_filt_x, right_filt_y, 1)

    # # info on coeff found
    # logg.debug(f"left_coeff: {left_coeff} right_coeff {right_coeff}")
    # left_yaw_deg = slope2deg(left_coeff[0])
    # right_yaw_deg = slope2deg(right_coeff[0])
    # logg.debug(f"left_yaw_deg: {left_yaw_deg} right_yaw_deg {right_yaw_deg} degrees")
    # left_yaw_rad = slope2rad(left_coeff[0])
    # right_yaw_rad = slope2rad(right_coeff[0])
    # logg.debug(f"left_yaw_rad: {left_yaw_rad} right_yaw_rad {right_yaw_rad} radians")

    # # plot results
    # fig, ax_points = plt.subplots(1, 1)
    # fig.set_size_inches((8, 8))
    # ax_points.set_title("Data in x-y parameter space")
    # ax_points.set_xlabel("x")
    # ax_points.set_ylabel("y")
    # # plot the laser dataset
    # style_points_all = {"ls": "", "marker": ".", "color": "k"}
    # ax_points.plot(left_filt_x, left_filt_y, **style_points_all)
    # ax_points.plot(right_filt_x, right_filt_y, **style_points_all)
    # ax_points.plot(0, 0, **style_points_all)
    # # plot fitted line
    # left_fit_y = np.polyval(left_coeff, left_filt_x)
    # right_fit_y = np.polyval(right_coeff, right_filt_x)
    # ax_points.plot(left_filt_x, left_fit_y)
    # ax_points.plot(right_filt_x, right_fit_y)

    return left_coeff, right_coeff


def dist_line_point(l_x, l_y, l_rad, orig_x=0, orig_y=0):
    """Computes the distance between a line and a point
    """
    # find the direction LP
    # lp_rad = math.atan((l_y - orig_y) / (l_x - orig_x))
    lp_rad = math.atan2(l_y - orig_y, l_x - orig_x)
    # find the angle between line and LP
    rel_lp_rad = l_rad - lp_rad
    # the distance between L and P
    lp_dist = dist_2D(l_x, l_y, orig_x, orig_y)
    # distance from line l to P
    dist = lp_dist * math.cos(rel_lp_rad)

    logg = logging.getLogger(f"c.{__name__}.dist_line_point")
    # recap = f"lp_rad: {lp_rad:.6f}"
    recap = f"lp_rad: {math.degrees(lp_rad):.6f}"
    # recap += f" rel_lp_rad {rel_lp_rad:.6f}"
    recap += f" rel_lp_rad: {math.degrees(rel_lp_rad):.6f}"
    recap += f" lp_dist {lp_dist:.6f}"
    recap += f" dist {dist:.6f}"
    logg.debug(recap)

    return dist


def compute_hough_pt(
    pt_x, pt_y, th_values,
):
    """For a single point, compute the distance between all the rotated lines passing
    through it and the origin

    returns an array with th_values elements
    """
    # logg = logging.getLogger(f"c.{__name__}.compute_hough")
    # logg.debug(f"Start compute_hough")

    dist_all_th = np.zeros_like(th_values)

    # for each theta value
    for i_th, th in enumerate(th_values):
        # find the distance of this line from the origin
        dist_all_th[i_th] = dist_line_point(pt_x, pt_y, th)

    return dist_all_th


def compute_hough_pt_mat(pt_x, pt_y, th_values):
    """For a single point, compute the distance between all the rotated lines passing
    through it and the origin, using numpy functions
    """
    # logg = logging.getLogger(f"c.{__name__}.compute_hough_pt_mat")
    # logg.debug(f"Start compute_hough_pt_mat")

    # the distance between L and P
    LP_dist = dist_2D(pt_x, pt_y, 0, 0)
    # the direction LP (P is 0,0 now)
    LP_rad = np.arctan2(pt_y, pt_x)
    # the angle between all lines l and LP
    rel_LP_rad = th_values - LP_rad
    # distance from all lines l to P
    dist_all_th = LP_dist * np.sin(rel_LP_rad)

    return dist_all_th


def do_hough(data_x, data_y, th_values):
    """For each point given, computes the distance between the rotated lines

    returns a list with data_x.shape[0] elements, each with th_values.shape[0] elements
    """
    # logg = logging.getLogger(f"c.{__name__}.do_hough")
    # logg.debug(f"Start do_hough")

    all_pt_dist_all_th = []

    # for i in [0, 10, 20, 30]:
    # for i in range(0, data_x.shape[0], 10):
    for i in range(data_x.shape[0]):
        pt_x = data_x[i]
        pt_y = data_y[i]
        # dist_all_th = compute_hough_pt(
        #     pt_x, pt_y, th_values
        # )
        dist_all_th = compute_hough_pt_mat(pt_x, pt_y, th_values)
        all_pt_dist_all_th.append(dist_all_th)

    return all_pt_dist_all_th


def do_hough_mat(data_x, data_y, th_values):
    """For each point given, computes the distance between the rotated lines

    uses np functions
    """

    # distance from all points to the origin
    all_LP_dist = np.sqrt(np.square(data_x) + np.square(data_y))

    # direction from all points to origin
    all_LP_rad = np.arctan2(data_y, data_x)

    # use broadcasting to stretch the arrays into common shapes
    # https://numpy.org/devdocs/user/theory.broadcasting.html#figure-4
    all_rel_LP_rad = th_values[:, np.newaxis] - all_LP_rad

    sin_all_rel_LP_rad = np.sin(all_rel_LP_rad)

    # all_pt_dist_all_th = all_LP_dist * sin_all_rel_LP_rad
    all_pt_dist_all_th = np.multiply(all_LP_dist, sin_all_rel_LP_rad)

    # logg = logging.getLogger(f"c.{__name__}.do_hough_mat")
    # logg.debug(f"th_values.shape: {th_values.shape}")
    # logg.debug(f"all_LP_dist.shape: {all_LP_dist.shape}")
    # logg.debug(f"all_LP_rad.shape: {all_LP_rad.shape}")
    # logg.debug(f"all_rel_LP_rad.shape: {all_rel_LP_rad.shape}")
    # logg.debug(f"sin_all_rel_LP_rad.shape: {sin_all_rel_LP_rad.shape}")
    # logg.debug(f"all_pt_dist_all_th.shape: {all_pt_dist_all_th.shape}")

    return all_pt_dist_all_th.transpose()


def fill_bins(
    int_all_pt_dist_all_th, quant_r_min_dist, quant_r_max_dist, bins_pos, bins_neg
):
    """TODO: what is fill_bins doing?
    """
    logg = logging.getLogger(f"c.{__name__}.fill_bins")
    logg.debug(f"Start fill_bins")

    for _, dist_all_th in enumerate(int_all_pt_dist_all_th):
        # logg.debug(f"dist_all_th.shape: {dist_all_th.shape}")
        for i_th, dist in enumerate(dist_all_th):
            if quant_r_min_dist <= dist <= quant_r_max_dist:
                r_bin = dist - quant_r_min_dist
                # logg.debug(f"i_th: {i_th} r_bin {r_bin}")
                bins_pos[i_th][r_bin] += 1
            elif -quant_r_min_dist >= dist >= -quant_r_max_dist:
                r_bin = dist - quant_r_min_dist
                # logg.debug(f"i_th: {i_th} r_bin {r_bin}")
                bins_neg[i_th][r_bin] += 1

    return bins_pos, bins_neg


def find_best_bin(
    bins_pos, bins_neg, th_values, quant_r_min_dist, quant_r_max_dist, r_stride
):
    """TODO: what is find_best_bin doing?
    """
    logg = logging.getLogger(f"c.{__name__}.find_best_bin")
    logg.debug(f"Start find_best_bin")

    max_bin_pos = np.max(bins_pos)
    argmax_bin_pos = np.argmax(bins_pos)
    ind_argmax_pos = np.unravel_index(argmax_bin_pos, bins_pos.shape)
    logg.debug(f"max_bin_pos: {max_bin_pos}")
    logg.debug(f"argmax_bin_pos: {argmax_bin_pos}")
    logg.debug(f"ind_argmax_pos: {ind_argmax_pos}")
    max_bin_neg = np.max(bins_neg)
    argmax_bin_neg = np.argmax(bins_neg)
    ind_argmax_neg = np.unravel_index(argmax_bin_neg, bins_neg.shape)
    logg.debug(f"max_bin_neg: {max_bin_neg}")
    logg.debug(f"argmax_bin_neg: {argmax_bin_neg}")
    logg.debug(f"ind_argmax_neg: {ind_argmax_neg}")

    if max_bin_pos >= max_bin_neg:
        i_best_th, i_best_r = ind_argmax_pos
        best_th = th_values[i_best_th]
        best_r = (i_best_r + quant_r_min_dist) * r_stride
    else:
        i_best_th, i_best_r = ind_argmax_neg
        best_th = th_values[i_best_th]
        best_r = -(i_best_r + quant_r_min_dist) * r_stride

    return best_th, best_r


def find_hough(
    data_x, data_y, r_stride, r_min_dist, r_max_dist, th_bin_num,
):
    """Analyze the data and find the best line
    """
    logg = logging.getLogger(f"c.{__name__}.find_hough")
    logg.debug(f"Start find_hough")

    r_bin_num = math.floor((r_max_dist - r_min_dist) / r_stride)

    th_values = np.linspace(0, math.pi, th_bin_num, endpoint=False)

    # all_pt_dist_all_th = do_hough(
    #     data_x, data_y, th_values
    # )
    # find all the sinusoids
    all_pt_dist_all_th = do_hough_mat(data_x, data_y, th_values)
    logg.debug(f"all_pt_dist_all_th.shape: {all_pt_dist_all_th.shape}")

    # on the theta it is automatically quantized, the data is aligned to th_values
    # quantize the distances by dividing by r_stride and rounding
    quant_all_pt_dist_all_th = all_pt_dist_all_th / r_stride
    int_all_pt_dist_all_th = np.rint(quant_all_pt_dist_all_th).astype(np.int16)
    logg.debug(f"int_all_pt_dist_all_th.shape: {int_all_pt_dist_all_th.shape}")

    # keep track of where we see the lines
    # we *include* the min/max values for r, so we need an extra bin
    bins_pos = np.zeros((th_bin_num, r_bin_num + 1), dtype=np.uint16)
    bins_neg = np.zeros((th_bin_num, r_bin_num + 1), dtype=np.uint16)
    logg.debug(f"bins_pos.shape: {bins_pos.shape}")

    quant_r_min_dist = int(np.rint(r_min_dist / r_stride))
    quant_r_max_dist = int(np.rint(r_max_dist / r_stride))
    logg.debug(f"quant_r_min_dist: {quant_r_min_dist}")
    logg.debug(f"quant_r_max_dist: {quant_r_max_dist}")

    fill_bins(
        int_all_pt_dist_all_th, quant_r_min_dist, quant_r_max_dist, bins_pos, bins_neg
    )

    best_th, best_r = find_best_bin(
        bins_pos, bins_neg, th_values, quant_r_min_dist, quant_r_max_dist, r_stride
    )

    logg.debug(f"best_th: {best_th} best_r {best_r} pi-best_th {math.pi-best_th}")

    # return all_pt_dist_all_th, th_values
    # return quant_all_pt_dist_all_th, th_values
    return quant_all_pt_dist_all_th, int_all_pt_dist_all_th, th_values, best_th, best_r


def load_filer_data(data_file_name, sector_wid):
    """TODO: what is load_filer_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_filer_data")
    # logg.debug(f"Start load_filer_data")

    data = load_data(data_file_name)

    # extract the data
    # tot_ray_number = data["tot_ray_number"]
    # logg.debug(f"tot_ray_number: {tot_ray_number}")
    ranges = np.array(data["ranges"])
    range_min = data["range_min"]
    range_max = data["range_max"]
    angles_rad = np.array(data["scan_angles"])
    # odom_robot_pose = data["odom_robot_pose"]
    # odom_robot_yaw = data["odom_robot_yaw"]
    # logg.debug(f"odom_robot_yaw {odom_robot_yaw} relative {odom_robot_yaw-math.pi/2}")

    t_filt_start = timer()

    # filter the data from the lasers
    left_filt_x, left_filt_y, right_filt_x, right_filt_y = extract_filt_lr(
        sector_wid, ranges, angles_rad, range_min, range_max
    )

    t_filt_end = timer()
    logg.debug(f"Filtering took {t_filt_end-t_filt_start} seconds")

    return left_filt_x, left_filt_y, right_filt_x, right_filt_y, data


def run_analyze_laser_data(args):
    """TODO: What is analyze_laser_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_analyze_laser_data")
    logg.debug(f"Starting run_analyze_laser_data")

    ########################
    # set hough parameters #
    ########################

    # set sector_wid in degrees
    sector_wid_deg = 30
    sector_wid = math.floor(sector_wid_deg / 180 * 200)
    logg.debug(f"sector_wid: {sector_wid} degrees {sector_wid_deg}")

    # r dimension of the bins
    # r_stride = 0.05
    r_stride = 0.01
    # r_stride = 0.005
    r_min_dist = 0.1
    r_max_dist = 0.6

    # number of bins in the [0, 180) interval
    # th_bin_num = 36
    # th_bin_num = 180
    th_bin_num = 360
    # th_bin_num = 720

    #####################################
    # load the laser data and filter it #
    #####################################

    data_file_name = "laser_data_16707.txt"
    # data_file_name = "laser_data_straight.txt"

    left_filt_x, left_filt_y, right_filt_x, right_filt_y, data = load_filer_data(
        data_file_name, sector_wid
    )

    #############################################
    # standard fitting of two independent lines #
    #############################################

    t_fit_start = timer()
    left_coeff, right_coeff = fit_parallel_lines(
        left_filt_x, left_filt_y, right_filt_x, right_filt_y,
    )
    t_fit_end = timer()
    logg.debug(f"Fitting took {t_fit_end-t_fit_start} seconds")

    ###################
    # run hough lines #
    ###################

    t_analyze_start = timer()
    all_pt_dist_all_th, int_all_pt_dist_all_th, th_values, best_th, best_r = find_hough(
        left_filt_x, left_filt_y, r_stride, r_min_dist, r_max_dist, th_bin_num,
    )
    t_analyze_end = timer()
    logg.debug(f"Analyzing took {t_analyze_end-t_analyze_start} seconds")

    ################
    # plot results #
    ################

    # setup plot
    fig, ax = plt.subplots(1, 2)
    fig.set_size_inches((16, 8))
    ax_points = ax[0]
    ax_bins = ax[1]

    # setup ax_bins
    ax_bins.set_title("Data in r-theta parameter space")
    ax_bins.set_xlabel("theta")
    ax_bins.set_ylabel("r")
    # plot all the sinusoids
    style_int = {"ls": "", "marker": ".", "color": "c"}
    for dist_all_th in int_all_pt_dist_all_th:
        ax_bins.plot(th_values, dist_all_th, **style_int)
    style_sin = {"ls": "-", "marker": "", "color": "y"}
    for dist_all_th in all_pt_dist_all_th:
        ax_bins.plot(th_values, dist_all_th, **style_sin)

    # setup ax_points
    ax_points.set_title("Data in x-y parameter space")
    ax_points.set_xlabel("x")
    ax_points.set_ylabel("y")
    # plot the laser dataset
    style_points_all = {"ls": "", "marker": ".", "color": "k"}
    ax_points.plot(left_filt_x, left_filt_y, **style_points_all)
    ax_points.plot(right_filt_x, right_filt_y, **style_points_all)
    # plot the hough line
    line_coeff = rth2ab(best_r, best_th)
    line_y = np.polyval(line_coeff, left_filt_x)
    style_hough = {"ls": "-", "marker": "", "color": "r"}
    ax_points.plot(left_filt_x, line_y, **style_hough)
    # plot the fit line
    left_fit_y = np.polyval(left_coeff, left_filt_x)
    style_fit = {"ls": "-", "marker": "", "color": "b"}
    ax_points.plot(left_filt_x, left_fit_y, **style_fit)

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_analyze_laser_data(args)
