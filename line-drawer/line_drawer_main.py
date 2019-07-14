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
    parser.add_argument(
        "-ml",
        "--max_line_len",
        type=int,
        default=100,
        help="number of segments to generate",
    )
    parser.add_argument(
        "-nc", "--num_corners", type=int, default=100, help="number of pins"
    )
    parser.add_argument(
        "-os", "--output_size", type=int, default=50, help="output size"
    )
    parser.add_argument("-lw", "--line_weight", type=int, default=3, help="line weight")

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


def run_line_benchmarks(input_image):
    """
    """

    line_test = LinerTest(input_image)
    line_test.benchmark_bresenham_naive()
    line_test.benchmark_np_sum()
    line_test.benchmark_bresenham_mask()


def analyze_drawing(input_image):
    num_corners = 10
    output_size = 10
    #  output_size = 200
    max_line_len = 10
    line_weight = 5
    top_left_x = 230
    top_left_y = 210

    line_test = LinerTest(
        path_input=input_image,
        num_corners=num_corners,
        output_size=output_size,
        max_line_len=max_line_len,
        line_weight=line_weight,
        top_left_x=top_left_x,
        top_left_y=top_left_y,
    )

    line_test.analyze_drawing()


def test_find_next_pin(input_image):
    num_corners = 10
    output_size = 10
    max_line_len = 10
    line_weight = 5

    l = Liner(
        path_input=input_image,
        num_corners=num_corners,
        output_size=output_size,
        max_line_len=max_line_len,
        line_weight=line_weight,
    )

    #  print(f"l.img_residual\n{l.img_residual}")
    #  print(f"l.line_mask_weighted\n{l.line_mask_weighted}")

    l.find_next_pin()

    #  seg = 8, 9
    #  print(f"l.line_mask_weighted[{seg}]\n{l.line_mask_weighted[seg]}")


def test_get_line_mask(input_image):
    num_corners = 10
    output_size = 10
    max_line_len = 10
    line_weight = 5

    l = Liner(
        path_input=input_image,
        num_corners=num_corners,
        output_size=output_size,
        max_line_len=max_line_len,
        line_weight=line_weight,
    )

    seg = 1, 5
    l.get_line_mask(*seg)
    print(f"l.line_mask[{seg}]\n{l.line_mask[seg]}")
    print(f"l.line_mask_weighted[{seg}]\n{l.line_mask_weighted[seg]}")


def test_add_segment(input_image):
    num_corners = 10
    output_size = 10
    max_line_len = 10
    line_weight = 5

    l = Liner(
        path_input=input_image,
        num_corners=num_corners,
        output_size=output_size,
        max_line_len=max_line_len,
        line_weight=line_weight,
    )

    #  seg = 1, 5
    #  l.get_line_mask(*seg)
    #  print(f"l.line_mask[{seg}]\n{l.line_mask[seg]}")
    #  print(f"l.line_mask_weighted[{seg}]\n{l.line_mask_weighted[seg]}")

    print(f"l.img_residual\n{l.img_residual}")
    print(f"l.line_mask_weighted\n{l.line_mask_weighted}")

    end_pin = 1
    l.add_segment(end_pin)
    print(f"l.line_mask_weighted\n{l.line_mask_weighted}")
    print(f"l.img_built\n{l.img_built}")
    print(f"l.img_residual\n{l.img_residual}")


def test_generate_line(input_image):
    output_size = 100
    #  output_size = 200
    #  num_corners = 10
    #  num_corners = 50
    #  num_corners = 100
    num_corners = output_size * 2
    #  max_line_len = 10
    #  max_line_len = 100
    max_line_len = 3000
    #  line_weight = 5
    line_weight = 3

    l = LinerTest(
        path_input=input_image,
        num_corners=num_corners,
        output_size=output_size,
        max_line_len=max_line_len,
        line_weight=line_weight,
    )

    l.generate_line()
    #  print(f"l.img_residual\n{l.img_residual}")
    #  print(f"l.img_built\n{l.img_built}")
    #  print(f"l.img_masked\n{l.img_masked}")
    formatter = ":4d"
    print("masked")
    print(l.get_str_mat(l.img_masked, formatter))
    print("residual")
    print(l.get_str_mat(l.img_residual, formatter))
    print("built")
    print(l.get_str_mat(l.img_built, formatter))

    l.save_img_built()


def main():
    args = setup()

    #  l = Liner(args.input_image)

    #  run_line_benchmarks(args.input_image)
    #  analyze_drawing(args.input_image)

    #  test_get_line_mask(args.input_image)
    #  test_add_segment(args.input_image)
    #  test_find_next_pin(args.input_image)
    test_generate_line(args.input_image)


if __name__ == "__main__":
    main()
