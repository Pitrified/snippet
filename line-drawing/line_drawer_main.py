import argparse

from timeit import default_timer as timer
from random import seed
from numpy.random import seed as npseed
from os import popen

from line_drawer_creator import liner

def parse_arguments():
    # setup parser
    parser = argparse.ArgumentParser(
            description='Find longest common subsequence of two strings',
            )

    parser.add_argument('-i', "--input_image",
            type=str,
            default='hp.jpg',
            help="path to input image to use")

    parser.add_argument('-o', "--output_image",
            type=str,
            default='out_img.jpg',
            help="path to output image")

    parser.add_argument('-s', "--seed",
            type=int,
            default=-1,
            help="random seed to use")

    # last line to parse the args
    args = parser.parse_args()
    return args

def test_creator(path_input, path_output):
    #  theline = liner(path_input, path_output)
    #  theline.test_line_shading()

    theline = liner(path_input, path_output,
            num_corners=300,
            output_size=600,
            )
    #  theline.test_pins_line(4000)
    theline.test_pins_line(8000)
    #  theline.compute_line()

def main():
    args = parse_arguments()
    #  print(args)

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int( timer() * 1e9 % 2**32 )
    else:
        myseed = args.seed
    seed(myseed)
    npseed(myseed)

    path_input = args.input_image
    path_output = args.output_image

    print(f'python3 line_drawer_main.py -s {myseed} -i {path_input} -o {path_output}')

    test_creator(path_input, path_output)

if __name__ == '__main__':
    main()
