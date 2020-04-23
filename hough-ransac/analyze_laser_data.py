import argparse
import json
import logging
import math
import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path
from random import seed as rseed
from timeit import default_timer as timer


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


def plot_add_create(x, y, show=False, ax=None, **kwargs):
    """TODO: what is plot_add_create doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.plot_add_create")
    # logg.debug(f"Start plot_add_create")

    if ax is None:
        fig, ax = plt.subplots(1, 1)

    ax.plot(x, y, **kwargs)

    if show:
        plt.show()

    return ax


def slope2deg(slope, direction=1):
    """Convert the slope of a line to an angle in degrees
    """
    return math.degrees(np.arctan2(slope, direction))


def slope2rad(slope, direction=1):
    """Convert the slope of a line to an angle in radians
    """
    return np.arctan2(slope, direction)


def polar_to_cartesian(ranges, angles_rad, dyaw=0, dx=0, dy=0):
    """TODO: what is polar_to_cartesian doing?
    """
    logg = logging.getLogger(f"c.{__name__}.polar_to_cartesian")
    # logg.debug(f"Start polar_to_cartesian")
    logg.debug(f"Polar to cartesian dyaw: {dyaw} dx: {dx} dy: {dy}")

    cosens = np.cos(angles_rad + dyaw)
    sins = np.sin(angles_rad + dyaw)

    x = np.multiply(ranges, cosens) + dx
    y = np.multiply(ranges, sins) + dy

    return x, y


def slice_data(center, sector_wid, *data):
    """TODO: what is slice_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.slice_data")
    logg.debug(f"Start slice_data")

    slice_ = slice(center - sector_wid, center + sector_wid)
    logg.debug(f"slice_: {slice_}")
    sliced_data = []
    for arr in data:
        sliced_data.append(arr[slice_])
    return sliced_data


def load_data(data_file_name):
    """TODO: what is load_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_data")
    logg.debug(f"Start load_data")

    t_load_start = timer()

    # load the data
    main_dir = Path(__file__).resolve().parent
    # data_file = main_dir / "laser_data" / "laser_data_straight.txt"
    data_file = main_dir / "laser_data" / data_file_name
    with data_file.open() as fp:
        data = json.load(fp)
    logg.debug(f"data.keys(): {data.keys()}")

    t_load_end = timer()
    logg.debug(f"Loading took {t_load_end-t_load_start} seconds")

    return data


def extract_filt_lr(sector_wid, ranges, angles_rad, range_min, range_max):
    """TODO: what is extract_filt_lr doing?
    """
    logg = logging.getLogger(f"c.{__name__}.extract_filt_lr")
    logg.debug(f"Start extract_filt_lr")

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


def find_parallel_lines(left_filt_x, left_filt_y, right_filt_x, right_filt_y):
    """TODO: what is find_parallel_lines doing?
    """
    logg = logging.getLogger(f"c.{__name__}.find_parallel_lines")
    logg.debug(f"Start find_parallel_lines")

    left_coeff = np.polyfit(left_filt_x, left_filt_y, 1)
    left_fit_y = np.polyval(left_coeff, left_filt_x)
    right_coeff = np.polyfit(right_filt_x, right_filt_y, 1)
    right_fit_y = np.polyval(right_coeff, right_filt_x)
    logg.debug(f"left_coeff: {left_coeff} right_coeff {right_coeff}")
    left_yaw_deg = slope2deg(left_coeff[0])
    right_yaw_deg = slope2deg(right_coeff[0])
    logg.debug(f"left_yaw_deg: {left_yaw_deg} right_yaw_deg {right_yaw_deg} degrees")
    left_yaw_rad = slope2rad(left_coeff[0])
    right_yaw_rad = slope2rad(right_coeff[0])
    logg.debug(f"left_yaw_rad: {left_yaw_rad} right_yaw_rad {right_yaw_rad} radians")

    # plot filtered points
    style = {"ls": "", "marker": "."}
    ax = plot_add_create(left_filt_x, left_filt_y, **style)
    plot_add_create(0, 0, ax=ax, **style)
    plot_add_create(right_filt_x, right_filt_y, ax=ax, **style)

    # plot fitted line
    style = {"ls": "-", "marker": ""}
    plot_add_create(left_filt_x, left_fit_y, ax=ax, **style)
    ax.set_title("Fitted left/right data")
    plot_add_create(0, 0, ax=ax, **style)
    plot_add_create(right_filt_x, right_fit_y, ax=ax, **style)


def dist_2D(x0, y0, x1, y1):
    """TODO: what is dist_2D doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.dist_2D")
    # logg.debug(f"Start dist_2D")

    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


def dist_line_point(l_x, l_y, l_rad, pt_x=0, pt_y=0):
    """TODO: what is dist_line_point doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.dist_line_point")
    # logg.debug(f"Start dist_line_point")

    # find the direction LP
    # lp_rad = math.atan((l_y - pt_y) / (l_x - pt_x))
    lp_rad = math.atan2(l_y - pt_y, l_x - pt_x)
    # find the angle between line and LP
    rel_lp_rad = l_rad - lp_rad
    # the distance between L and P
    lp_dist = dist_2D(l_x, l_y, pt_x, pt_y)
    # distance from line l to P
    dist = lp_dist * math.sin(rel_lp_rad)

    # dist = abs(dist)

    return dist


def compute_hough_pt(pt_x, pt_y, bins, th_values, r_stride, r_min_dist, r_max_dist):
    """TODO: what is compute_hough doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.compute_hough")
    # logg.debug(f"Start compute_hough")

    dist_all = np.zeros_like(th_values)

    # for each theta value
    for i_th, th in enumerate(th_values):
        # find the distance of this line from the origin
        dist_all[i_th] = dist_line_point(pt_x, pt_y, th)

    return dist_all


def find_parallel_hough(left_filt_x, left_filt_y, right_filt_x, right_filt_y):
    """TODO: what is find_parallel_hough doing?
    """
    logg = logging.getLogger(f"c.{__name__}.find_parallel_hough")
    logg.debug(f"Start find_parallel_hough")

    # r dimension of the bins
    r_stride = 0.01
    r_min_dist = 0.1
    r_max_dist = 0.6
    r_bin_num = math.floor((r_max_dist - r_min_dist) / r_stride)

    # number of bins in the [0, 180) interval
    th_bin_num = 180
    th_values = np.linspace(0, math.pi, th_bin_num, endpoint=False)

    # keep track of where we see the lines
    bins = np.zeros((th_bin_num, r_bin_num), dtype=np.uint16)

    # setup plot
    fig, ax = plt.subplots(1, 2)
    fig.set_size_inches((16, 8))
    ax_bins = ax[0]
    ax_points = ax[1]
    style_bins = {"ls": "-", "marker": "", "color": "y"}
    style_points = {"ls": "", "marker": ".", "color": "r"}
    style_points_all = {"ls": "", "marker": ".", "color": "k"}
    ax_points.plot(left_filt_x, left_filt_y, **style_points_all)
    ax_points.plot(right_filt_x, right_filt_y, **style_points_all)

    # for i in [0, 10, 20, 30]:
    # for i in range(0, left_filt_x.shape[0], 10):
    for i in range(left_filt_x.shape[0]):
        pt_x = left_filt_x[i]
        pt_y = left_filt_y[i]
        dist_all = compute_hough_pt(
            pt_x, pt_y, bins, th_values, r_stride, r_min_dist, r_max_dist
        )
        ax_bins.plot(th_values, dist_all, **style_bins)
        ax_points.plot(pt_x, pt_y, **style_points)


def run_analyze_laser_data(args):
    """TODO: What is analyze_laser_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_analyze_laser_data")
    logg.debug(f"Starting run_analyze_laser_data")

    # data_file_name = "laser_data_16707.txt"
    data_file_name = "laser_data_straight.txt"
    data = load_data(data_file_name)

    tot_ray_number = data["tot_ray_number"]
    logg.debug(f"tot_ray_number: {tot_ray_number}")

    ranges = np.array(data["ranges"])
    range_min = data["range_min"]
    range_max = data["range_max"]
    angles_rad = np.array(data["scan_angles"])
    # odom_robot_pose = data["odom_robot_pose"]
    odom_robot_yaw = data["odom_robot_yaw"]
    logg.debug(f"odom_robot_yaw {odom_robot_yaw} relative {odom_robot_yaw-math.pi/2}")

    # how many rays to consider each side, around the center of the beam
    sector_wid = 50

    # set sector_wid in degrees
    sector_wid_deg = 30
    sector_wid = math.floor(sector_wid_deg / 180 * 200)
    logg.debug(f"sector_wid: {sector_wid} degrees {sector_wid_deg}")

    t_analyze_start = timer()

    left_filt_x, left_filt_y, right_filt_x, right_filt_y = extract_filt_lr(
        sector_wid, ranges, angles_rad, range_min, range_max
    )

    # find_parallel_lines(left_filt_x, left_filt_y, right_filt_x, right_filt_y)
    find_parallel_hough(left_filt_x, left_filt_y, right_filt_x, right_filt_y)

    t_analyze_end = timer()
    logg.debug(f"Analyzing took {t_analyze_end-t_analyze_start} seconds")

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_analyze_laser_data(args)
