import argparse
import logging

import numpy as np

from random import seed
from timeit import default_timer as timer

from doodle_agent import Agent
from doodle_map import DoodleMap


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument("-s", "--seed", type=int, default=-1, help="random seed to use")

    parser.add_argument("-b", "--bias", type=float, default=0.1, help="curvature bias")
    parser.add_argument("-c", "--scale", type=float, default=1, help="curvature scale")
    parser.add_argument("-l", "--step_len", type=float, default=5, help="step lenght")

    parser.add_argument("-w", "--width", type=int, default=100, help="map width")
    parser.add_argument("-e", "--height", type=int, default=100, help="map height")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="hp.bmp",
        help="path to input map to use, BW image",
    )

    parser.add_argument(
        "-o",
        "--path_output",
        type=str,
        default="out.jpg",
        help="path to output image",
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
    log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def run(bias, step_len,scale,  width, height, path_output):
    # init here the preexisting map if needed
    dm = DoodleMap(width, height)

    # there can be more than one agent on a map
    ag = Agent(dm, bias, scale, step_len)

    n = 1000
    try:
        for i in range(n):
            ag.step()
    except IndexError:
        pass

    dm.save(path_output)


def main():
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.seed
    seed(myseed)
    np.random.seed(myseed)

    path_input = args.path_input
    path_output = args.path_output
    bias = args.bias
    scale = args.scale
    step_len = args.step_len
    width = args.width
    height = args.height

    recap = f"python3 doodle_main.py"
    recap += f" --seed {myseed}"
    recap += f" --bias {bias}"
    recap += f" --scale {scale}"
    recap += f" --step_len {step_len}"
    recap += f" --width {width}"
    recap += f" --height {height}"
    recap += f" --path_input {path_input}"
    recap += f" --path_output {path_output}"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    run(bias, step_len, scale, width, height, path_output)


if __name__ == "__main__":
    main()
