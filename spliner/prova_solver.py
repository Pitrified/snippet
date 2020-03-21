import argparse
import logging

import numpy as np
import matplotlib.pyplot as plt

from random import seed as rseed
from timeit import default_timer as timer

import utils


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
    rseed(myseed)
    np.random.seed(myseed)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 prova_solver.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def cubic_curve(x0, y0, y0p, x1, y1, y1p):
    logg = logging.getLogger(f"c.{__name__}.cubic_curve")
    logg.debug(f"Starting cubic_curve")

    A = np.array(
        [
            [x0 ** 3, x0 ** 2, x0, 1],
            [3 * x0 ** 2, 2 * x0 ** 1, 1, 0],
            [x1 ** 3, x1 ** 2, x1, 1],
            [3 * x1 ** 2, 2 * x1 ** 1, 1, 0],
        ]
    )
    b = np.array([y0, y0p, y1, y1p])
    x = np.linalg.solve(A, b)

    logg.debug(f"x: {x}")
    logg.debug(f"y = {x[0]:.4f}*x^3 + {x[1]:.4f}*x^2 + {x[2]:.4f}*x + {x[3]:.4f}")

    return x


def run_prova_solver(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_prova_solver")
    logg.debug(f"Starting run_prova_solver")

    # create the plot
    fig, ax = plt.subplots()
    # sample per segment
    num_samples = 100

    # first segment
    x0, y0, y0p = 1, 1, 0
    x1, y1, y1p = 3, 2, 1
    coeff = cubic_curve(x0, y0, y0p, x1, y1, y1p)

    x_sample = np.linspace(x0, x1, num_samples)
    y_segment = utils.poly_model(x_sample, np.flip(coeff))
    utils.add_points(x_sample, y_segment, ax)

    # second segment
    x0, y0, y0p = 3, 2, 1
    #  x1, y1, y1p = 4, 4, 2
    x1, y1, y1p = 3.5, 3.5, 6
    coeff = cubic_curve(x0, y0, y0p, x1, y1, y1p)

    x_sample = np.linspace(x0, x1, num_samples)
    y_segment = utils.poly_model(x_sample, np.flip(coeff))
    utils.add_points(x_sample, y_segment, ax, color="r")

    # plot everything
    utils.plot_build(fig, ax)
    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_prova_solver(args)
