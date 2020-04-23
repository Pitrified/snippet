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


def scatter_plot(x, y, show=True, ax=None, **kwargs):
    """TODO: what is scatter_plot doing?
    """
    logg = logging.getLogger(f"c.{__name__}.scatter_plot")
    logg.debug(f"Start scatter_plot")

    if ax is None:
        fig, ax = plt.subplots(1, 1)

    ax.plot(x, y, **kwargs)

    if show:
        plt.show()

    return ax


def polar_to_cartesian(ranges, angles_rad, dyaw=0, dx=0, dy=0):
    """TODO: what is polar_to_cartesian doing?
    """
    logg = logging.getLogger(f"c.{__name__}.polar_to_cartesian")
    logg.debug(f"Start polar_to_cartesian")

    cosens = np.cos(angles_rad + dyaw)
    sins = np.sin(angles_rad + dyaw)

    x = np.multiply(ranges, cosens) + dx
    y = np.multiply(ranges, sins) + dy

    return x, y


def run_analyze_laser_data(args):
    """TODO: What is analyze_laser_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_analyze_laser_data")
    logg.debug(f"Starting run_analyze_laser_data")

    # load the data
    main_dir = Path(__file__).resolve().parent
    data_file = main_dir / "laser_data" / "laser_data_straight.txt"
    with data_file.open() as fp:
        data = json.load(fp)
    logg.debug(f"data.keys(): {data.keys()}")

    tot_ray_number = data["tot_ray_number"]
    logg.debug(f"tot_ray_number: {tot_ray_number}")

    ranges = data["ranges"]
    scan_angles = data["scan_angles"]

    width = 50
    left_center = 300
    left_slice = slice(left_center - width, left_center + width)
    left_ranges = np.array(ranges[left_slice])
    left_angles_rad = np.array(scan_angles[left_slice])
    left_angles_deg = left_angles_rad * 180 / math.pi
    left_pairs = np.vstack((left_ranges, left_angles_deg)).transpose()

    left_mean = np.mean(left_ranges)
    left_max = np.max(left_ranges)
    left_min = np.min(left_ranges)
    logg.debug(f"left_mean: {left_mean} left_max: {left_max} left_min: {left_min}")
    logg.debug(f"left_pairs: shape {left_pairs.shape}\n{left_pairs}")

    left_x, left_y = polar_to_cartesian(left_ranges, left_angles_rad)
    logg.debug(f"left_x: shape {left_x.shape}\n{left_x}")

    right_center = 100
    right_slice = slice(right_center - width, right_center + width)
    right_ranges = np.array(ranges[right_slice])
    right_angles_rad = np.array(scan_angles[right_slice])
    right_angles_deg = right_angles_rad * 180 / math.pi
    right_pairs = np.vstack((right_ranges, right_angles_deg)).transpose()

    right_mean = np.mean(right_ranges)
    right_max = np.max(right_ranges)
    right_min = np.min(right_ranges)
    logg.debug(f"right_mean: {right_mean} max: {right_max} min: {right_min}")
    logg.debug(f"right_pairs: shape {right_pairs.shape}\n{right_pairs}")

    right_x, right_y = polar_to_cartesian(right_ranges, right_angles_rad)
    logg.debug(f"right_x: shape {right_x.shape}\n{right_x}")

    # style = {"ls": "", "marker": "."}
    style = {"ls": "-", "marker": "."}
    ax = scatter_plot(left_x, left_y, show=False, **style)
    ax = scatter_plot(0, 0, ax=ax, show=False, **style)
    scatter_plot(right_x, right_y, ax=ax, **style)


if __name__ == "__main__":
    args = setup_env()
    run_analyze_laser_data(args)
