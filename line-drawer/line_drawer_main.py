import argparse
import logging
import numpy as np

from os import popen
from random import seed
from timeit import default_timer as timer

from line_drawer_creator import Liner
from line_drawer_test import LinerTest


def parse_arguments():
    # setup parser
    parser = argparse.ArgumentParser(description="Approximate an image using a line")

    parser.add_argument(
        "-i",
        "--input_image",
        type=str,
        default="hp.jpg",
        help="path to input image to use",
    )

    parser.add_argument(
        "-o",
        "--output_image",
        type=str,
        default="out_img.png",
        help="path to output image",
    )

    parser.add_argument("-s", "--seed", type=int, default=-1, help="random seed to use")

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logmoduleconsole = logging.getLogger(f"{__name__}.console")
    logmoduleconsole.propagate = False
    logmoduleconsole.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logmoduleconsole.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logmoduleconsole.log(5, 'Exceedingly verbose debug')

    return logmoduleconsole


def setup():
    args = parse_arguments()

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.seed
    seed(myseed)
    np.random.seed(myseed)

    path_input = args.input_image
    path_output = args.output_image

    setup_logger()

    # RIP logger
    print(f"python3 line_drawer_main.py -s {myseed} -i {path_input} -o {path_output}")

    return args


def test_the_test_class(input_image):
    """
    """

    line_test = LinerTest(input_image)
    line_test.benchmark_bresenham_np()


def main():
    args = setup()

    test_the_test_class(args.input_image)


if __name__ == "__main__":
    main()
