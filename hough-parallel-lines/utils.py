import json
import logging
import math
import numpy as np

from pathlib import Path
from timeit import default_timer as timer


def dist_2D(x0, y0, x1, y1):
    """Computes the 2D distance between two points
    """
    # logg = logging.getLogger(f"c.{__name__}.dist_2D")
    # logg.debug(f"Start dist_2D")

    return math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)


def load_data(data_file_name):
    """Load the data from a .json file
    """
    logg = logging.getLogger(f"c.{__name__}.load_data")
    # logg.debug(f"Start load_data")

    t_load_start = timer()

    # load the data
    main_dir = Path(__file__).resolve().parent
    # data_file = main_dir / "laser_data" / "laser_data_straight.txt"
    data_file = main_dir / "laser_data" / data_file_name
    with data_file.open() as fp:
        data = json.load(fp)
    # logg.debug(f"data.keys(): {data.keys()}")

    # logg.debug(f"data['odom_robot_yaw']: {data['odom_robot_yaw']}")

    t_load_end = timer()
    logg.debug(f"Loading took {t_load_end-t_load_start} seconds")

    return data


def slope2deg(slope, direction=1):
    """Convert the slope of a line to an angle in degrees
    """
    return math.degrees(np.arctan2(slope, direction))


def slope2rad(slope, direction=1):
    """Convert the slope of a line to an angle in radians
    """
    return np.arctan2(slope, direction)


def rth2ab(r, th):
    """TODO: what is rth2ab doing?
    """
    logg = logging.getLogger(f"c.{__name__}.rth2ab")
    logg.debug(f"Start rth2ab")

    norm_th = th - math.pi / 2
    x = math.cos(norm_th) * r
    y = math.sin(norm_th) * r

    a = math.tan(th)
    b = y - a * x

    return np.array([a, b])


def polar_to_cartesian(ranges, angles_rad, dyaw=0, dx=0, dy=0):
    """Converts points in (range, angle) polar coord to cartesian

    Can translate and rotate them
    """
    # logg = logging.getLogger(f"c.{__name__}.polar_to_cartesian")
    # logg.debug(f"Start polar_to_cartesian")
    # logg.debug(f"Polar to cartesian dyaw: {dyaw} dx: {dx} dy: {dy}")

    cosens = np.cos(angles_rad + dyaw)
    sins = np.sin(angles_rad + dyaw)

    x = np.multiply(ranges, cosens) + dx
    y = np.multiply(ranges, sins) + dy

    return x, y
