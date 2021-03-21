import argparse
import logging

import numpy as np

from random import seed
from timeit import default_timer as timer

from bresenham_line import Bresenham
from bresenham_generator import bresenham_generator
from bresenham_generator import setup_logger_generator


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--input_path",
        type=str,
        default="hp.jpg",
        help="path to input image to use",
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


def test_creation(width, height, logLevel="INFO"):
    """Create an instance of Bresenham
    """
    logcreate = logging.getLogger(f"{__name__}.console.create")
    logcreate.setLevel(logLevel)

    bre = Bresenham(width, height)
    logcreate.debug("\n" + bre.getstr_map_noc())


def test_line(width, height, x0, y0, x1, y1, logLevel="INFO"):

    logline = logging.getLogger(f"{__name__}.console.line")
    logline.setLevel(logLevel)

    bre = Bresenham(width, height)

    bre.add_line(x0, y0, x1, y1)

    logline.debug("\n" + bre.getstr_map_noc())


def test_lines(width, height, logLevel="INFO"):

    logline = logging.getLogger(f"{__name__}.console.lines")
    logline.setLevel(logLevel)

    bre = Bresenham(width, height)

    x0, y0 = (10, 10)

    x1, y1 = (14, 18)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)
    x1, y1 = (18, 14)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)

    x1, y1 = (6, 18)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)
    x1, y1 = (2, 14)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)

    x1, y1 = (2, 8)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)
    x1, y1 = (6, 2)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)

    x1, y1 = (14, 2)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)
    x1, y1 = (18, 8)
    logline.debug(f"Line ({x0}, {y0}) to ({x1}, {y1})")
    bre.add_line(x0, y0, x1, y1)

    logline.info("\n" + bre.getstr_map_noc())


def test_bresenham():
    """Test Bresenham algorithm
    """
    test_creation(10, 20, "DEBUG")
    x0, y0 = (0, 0)
    x1, y1 = (4, 8)
    #  test_line(10, 10, x0, y0, x1, y1, 'DEBUG')

    test_lines(20, 20, "DEBUG")
    #  test_lines(20, 20, 'INFO')


def test_bresenham_generator():
    """Test the generator
    """

    setup_logger_generator()

    logLevel = "DEBUG"
    logline = logging.getLogger(f"{__name__}.console.gen_test")
    logline.setLevel(logLevel)

    x0, y0 = 2, 2
    x1, y1 = 4, 8
    for x, y in bresenham_generator(x0, y0, x1, y1):
        logline.info(f"x {x} y {y}")

    x1, y1 = 2, 2
    for x, y in bresenham_generator(x0, y0, x1, y1):
        logline.info(f"x {x} y {y}")


def benchmark_bresenham_generator():
    """Evaluate the performance
    """
    logLevel = "DEBUG"
    logline = logging.getLogger(f"{__name__}.console.gen_test")
    logline.setLevel(logLevel)

    x0, y0 = 2, 2
    n = int(1e6)
    x1, y1 = 4 * n, 8 * n + 1
    points = 0

    start = timer()
    for x, y in bresenham_generator(x0, y0, x1, y1):
        points += 1
    end = timer()
    gen_time = end - start

    p = 0
    start_add = timer()
    for _ in range(points):
        p += 1
    end_add = timer()
    add_time = end_add - start_add
    logline.info(f"Time to sum {points} points: {add_time:.4f} s")

    tot_time = gen_time - add_time
    logline.info(f"Time to generate {points} points: {tot_time:.4f} s")


def main():
    args = parse_arguments()

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.seed
    seed(myseed)
    np.random.seed(myseed)

    path_input = args.input_path

    logmoduleconsole = setup_logger()
    logmoduleconsole.info(f"python3 bresenham_main.py -s {myseed} -i {path_input}")

    #  test_bresenham()

    #  test_bresenham_generator()
    benchmark_bresenham_generator()


if __name__ == "__main__":
    main()
