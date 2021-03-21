import argparse
import logging
import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
import math

from random import seed as rseed
from timeit import default_timer as timer

from typing import Tuple


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
    recap = f"python3 create_laser_data.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def compute_rot_matrix(theta_deg: float) -> np.ndarray:
    """Compute the 2x2 rotation matrix for angle theta_deg in degrees
    """
    logg = logging.getLogger(f"c.{__name__}.compute_rot_matrix")
    logg.setLevel("INFO")

    theta_deg = math.radians(theta_deg)
    ct = math.cos(theta_deg)
    st = math.sin(theta_deg)
    rot_mat = np.array(((ct, -st), (st, ct)))
    logg.debug(f"rot_mat = {rot_mat}")

    return rot_mat


def rotate_point(point: np.ndarray, theta_deg: float) -> np.ndarray:
    """Rotate a point (or Nx2 array of points) by theta_deg degree

    MAYBE automagically transpose the point mat if it is 2xN instead of Nx2
    """
    rot_mat = compute_rot_matrix(theta_deg)
    return np.matmul(point, rot_mat)


def create_laser_data(
    th_center_deg: float,
    th_delta_deg: float,
    th_num: int,
    laser_std_dev: float,
    th_rot_deg: float,
    corridor_width: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """TODO: what is create_laser_data doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.create_laser_data")
    # logg.debug(f"Start create_laser_data")

    half_cor_wid = corridor_width / 2
    # fig, ax = plt.subplots(1, 1)
    # fig.set_size_inches((10, 8))

    th_min = math.radians(th_center_deg - th_delta_deg)
    th_max = math.radians(th_center_deg + th_delta_deg)
    th_values = np.linspace(th_min, th_max, th_num)

    # and the distance of the perfect sensor
    wall_x = half_cor_wid / np.tan(th_values)
    wall_y = np.ones_like(th_values) * half_cor_wid
    wall_dist = np.sqrt(np.square(wall_x) + np.square(wall_y))

    # plot original points
    # st = {"ls": "", "marker": ".", "color": "r"}
    # ax.plot(wall_x, wall_y, **st)

    # add gaussian noise to the distances
    mean = 0
    noise = np.random.normal(mean, laser_std_dev, wall_dist.shape[0])
    wall_dist_noisy = wall_dist + noise
    wall_noisy_x = np.cos(th_values) * wall_dist_noisy
    wall_noisy_y = np.sin(th_values) * wall_dist_noisy

    # st = {"ls": "", "marker": ".", "color": "g"}
    # ax.plot(wall_noisy_x, wall_noisy_y, **st)
    # ax.plot(0, 0, **st)

    wall_data = np.vstack((wall_noisy_x, wall_noisy_y))
    rot_wall_data = rotate_point(wall_data.T, th_rot_deg)
    rot_wall_data = rot_wall_data.T
    return rot_wall_data[0], rot_wall_data[1]


def run_create_laser_data(args: argparse.Namespace):
    """TODO: What is create_laser_data doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_create_laser_data")
    logg.debug(f"Starting run_create_laser_data")

    # get the direction of the rays
    th_center_deg = 90
    th_delta_deg = 45
    th_num = 201
    laser_std_dev = 0.01
    th_rot_deg = 0
    corridor_width = 0.56

    left_filt_x, left_filt_y = create_laser_data(
        th_center_deg, th_delta_deg, th_num, laser_std_dev, th_rot_deg, corridor_width
    )

    th_center_deg += 180
    right_filt_x, right_filt_y = create_laser_data(
        th_center_deg, th_delta_deg, th_num, laser_std_dev, th_rot_deg, corridor_width
    )

    fig, ax = plt.subplots(1, 1)
    fig.set_size_inches((8, 8))
    st = {"ls": "", "marker": ".", "color": "k"}
    ax.plot(left_filt_x, left_filt_y, **st)
    ax.plot(right_filt_x, right_filt_y, **st)
    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_create_laser_data(args)
