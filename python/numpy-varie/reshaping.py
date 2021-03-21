import argparse
import logging

import numpy as np

from random import seed
from timeit import default_timer as timer


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

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

    # example log line
    logg = logging.getLogger(f"c.{__name__}.setup_logger")
    logg.debug(f"Done setting up logger")


def setup_env():
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.rand_seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.rand_seed
    seed(myseed)
    np.random.seed(myseed)

    # build command string to repeat this run
    recap = f"python3 lab03_main.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_reshaping(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_reshaping")
    logg.debug(f"Reshaping experiments")

    n = 3
    unrolled = np.arange(n * n * 2).reshape(2, n * n)
    logg.debug(f"unrolled: shape {unrolled.shape}\n{unrolled}")

    squared = unrolled.reshape(n, n, 2)
    logg.debug(f"squared: shape {squared.shape}\n{squared}")
    logg.debug(f"squared[0,0] = {squared[0,0]}")
    logg.debug(f"squared[2,0] = {squared[2,0]}")
    logg.debug(f"squared[0,2] = {squared[0,2]}")

    squared0 = unrolled[0].reshape(n, n)
    logg.debug(f"squared0: shape {squared0.shape}\n{squared0}")

    wrapped = np.zeros((n, n, 2), dtype=np.uint8)
    wrapped[:, :, 0] = unrolled[0].reshape(n, n)
    wrapped[:, :, 1] = unrolled[1].reshape(n, n)
    logg.debug(f"wrapped: shape {wrapped.shape}\n{wrapped}")
    logg.debug(f"wrapped[0,0] = {wrapped[0,0]}")
    logg.debug(f"wrapped[2,0] = {wrapped[2,0]}")
    logg.debug(f"wrapped[0,2] = {wrapped[0,2]}")

    wrapped_bis = unrolled.transpose().reshape(n, n, 2)
    logg.debug(f"wrapped_bis: shape {wrapped_bis.shape}\n{wrapped_bis}")
    logg.debug(f"wrapped_bis[0,0] = {wrapped_bis[0,0]}")
    logg.debug(f"wrapped_bis[2,0] = {wrapped_bis[2,0]}")
    logg.debug(f"wrapped_bis[0,2] = {wrapped_bis[0,2]}")

    for s_pos in wrapped[:, :]:
        logg.debug(f"s_pos {s_pos.shape}\n{s_pos}")

    for row in wrapped:
        logg.debug(f"row {row.shape}")
        for s_pos in row:
            logg.debug(f"s_pos {s_pos.shape} : {s_pos}")


def run_lidar(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_lidar")
    logg.debug(f"Reshaping run_lidar")

    ray_sensors_per_ray = 10  # number of sensors along a ray
    ray0 = tuple((s, 0) for s in range(1, ray_sensors_per_ray + 1))
    ray0 = np.array(ray0).transpose()
    ray1 = tuple((s, 1) for s in range(11, ray_sensors_per_ray + 11))
    ray1 = np.array(ray1).transpose()
    ray2 = tuple((s, 2) for s in range(21, ray_sensors_per_ray + 21))
    ray2 = np.array(ray2).transpose()
    logg.debug(f"shape ray0 {ray0.shape}")
    logg.debug(f"ray0\n{ray0}")
    logg.debug(f"ray1\n{ray1}")
    logg.debug(f"ray2\n{ray2}")
    sat = []
    sat.append(ray0)
    sat.append(ray1)
    sat.append(ray2)
    sat = np.array(sat)
    logg.debug(f"shape sensor_array_template {sat.shape}")
    logg.debug(f"sat\n{sat}")

    #  sat = sat.transpose((0,2,1))
    sat = sat.transpose((1, 0, 2))
    logg.debug(f"shape transposed {sat.shape}")
    logg.debug(f"sat\n{sat}")

    sat = sat.reshape(2, ray_sensors_per_ray * 3)
    logg.debug(f"shape reshaped {sat.shape}")
    logg.debug(f"sat\n{sat}")

    sat = sat.transpose()
    logg.debug(f"shape transposed again {sat.shape}")
    logg.debug(f"sat\n{sat}")
    logg.debug(f"sat[0]: {sat[0]}")
    logg.debug(f"sat[15]: {sat[15]}")
    logg.debug(f"sat[26]: {sat[26]}")


if __name__ == "__main__":
    args = setup_env()
    #  run_reshaping(args)
    run_lidar(args)
