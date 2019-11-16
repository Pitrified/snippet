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

    for s_pos in wrapped[:,:]:
        logg.debug(f"s_pos {s_pos.shape}\n{s_pos}")

    for row in wrapped:
        logg.debug(f"row {row.shape}")
        for s_pos in row:
            logg.debug(f"s_pos {s_pos.shape} : {s_pos}")

if __name__ == "__main__":
    args = setup_env()
    run_reshaping(args)
