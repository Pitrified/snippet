import argparse
import logging
import math
import numpy as np  # type: ignore

from random import seed as rseed
from timeit import default_timer as timer


def parse_arguments():
    """Setup CLI interface"""
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
    """Setup logger that outputs to console for the module"""
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
    recap = f"python3 dotter.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_dotter(args):
    """TODO: What is dotter doing?"""
    logg = logging.getLogger(f"c.{__name__}.run_dotter")
    logg.debug(f"Starting run_dotter")

    radius: int = 10
    th_rad_inner = np.linspace(0, 2 * math.pi, num=9, endpoint=True)
    x = np.cos(th_rad_inner) * radius
    y = np.sin(th_rad_inner) * radius
    th_deg = np.degrees(th_rad_inner) + 90
    th_deg = np.where(th_deg >= 360, th_deg - 360, th_deg)
    points = np.vstack((x, y, th_deg)).T
    points = np.where(np.abs(points) < 1e-6, 0, points)

    for pt in points:
        # logg.debug(f"pt: {pt}")
        logg.debug(f"{pt[0]}\t{pt[1]}\t{pt[2]}")

    radius: int = 16
    th_rad_inner = np.linspace(math.pi / 2, math.pi / 2 + 2 * math.pi, num=17)
    x = np.cos(th_rad_inner) * radius
    y = np.sin(th_rad_inner) * radius
    th_deg = np.degrees(th_rad_inner) + 90
    th_deg = np.where(th_deg >= 360, th_deg - 360, th_deg)
    points = np.vstack((x, y, th_deg)).T
    points = np.where(np.abs(points) < 1e-6, 0, points)

    for pt in points:
        # logg.debug(f"pt: {pt}")
        logg.debug(f"{pt[0]}\t{pt[1]}\t{pt[2]}")


if __name__ == "__main__":
    args = setup_env()
    run_dotter(args)
