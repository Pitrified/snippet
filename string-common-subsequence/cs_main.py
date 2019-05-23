import resource, sys

import argparse

from timeit import default_timer as timer
from random import seed
from numpy.random import seed as npseed
from os import popen

from cs_finder import generate_string_by_len
from cs_finder import generate_similar_string_nonrepeating
from cs_finder import LCSfinder

def parse_arguments():
    # setup parser
    parser = argparse.ArgumentParser(
            description='Find longest common subsequence of two strings',
            )

    # positional args (mandatory)
    #  parser.add_argument('echo', help='echo this string')

    parser.add_argument('-r', "--rows",
            type=int,
            default=-1,
            help="HEIGHT of the map, number of rows, -1 or empty for auto")

    parser.add_argument('-c', "--columns",
            type=int,
            default=-1,
            help="WIDTH of the map, number of columns, -1 or empty for auto")

    parser.add_argument('-s', "--seed",
            type=int,
            default=-1,
            help="random seed to use")

    # last line to parse them
    args = parser.parse_args()

    #  parse the args even more if needed
    args_parsed = { a : v for a, v in args._get_kwargs() }
    return args_parsed

def test_generate_string():
    generate_string_by_len(10, 5)
    generate_string_by_len(10, 26)
    generate_string_by_len(10, 26*2)
    generate_string_by_len(10, 26*2+1)

def test_generate_similar_string_nonrepeating():
    generate_similar_string_nonrepeating(10)
    generate_similar_string_nonrepeating(100)

def test_lcs_base(rows, columns):
    '''Test lcs'''
    print(f'doing test_lcs_base r {rows} c {columns}')

    #  lenX = 10
    #  lenY = 10
    lenX = rows
    lenY = columns
    num_possible_chars = 4

    X = generate_string_by_len(lenX, num_possible_chars)
    Y = generate_string_by_len(lenY, num_possible_chars)
    #  X, Y = generate_similar_string_nonrepeating(10)
    #  X = ['A','B','C','D']
    #  Y = ['A','E','C','D']
    #  Y = ['A','C','E','D']

    #  print(f'X {X}\nY {Y}')

    finder = LCSfinder(X, Y)

    print(f'\nInput strings:\n{finder.get_str_input()}\n')

    finder.init_lcs()

    #  print(finder.get_str_B())

    #  cost, B = find_LCS(X, Y)
    finder.find_LCS()
    #  print(finder.get_str_B())
    #  print(finder.get_str_cost())
    print(finder.get_str_B_cost())
    print(finder.get_str_lcs())

    finder.check_is_cs()

    finder.print_stats()

def run_test_lcs_base(rows, columns):
    test_lcs_base(rows, columns)

def test_lcs_similar(length, errors):
    '''Test lcs'''
    print(f'\ndoing test_lcs_similar l {length} e {errors}')

    X, Y = generate_similar_string_nonrepeating(length, errors)

    finder = LCSfinder(X, Y)

    #  print(f'\nInput strings:\n{finder.get_str_input()}\n')

    finder.init_lcs()

    #  print(finder.get_str_B())

    finder.find_LCS()
    print(finder.get_str_B())
    #  print(finder.get_str_cost())
    #  print(finder.get_str_B_cost())
    #  print(finder.get_str_lcs())

    finder.check_is_cs()

def run_test_lcs_similar():
    #  length = 100
    length = 4000
    errors = 400
    test_lcs_similar(length, errors)

def main():
    # we destroy the stack like men https://stackoverflow.com/a/16248113
    #  resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))
    #  sys.setrecursionlimit(10**6)

    args = parse_arguments()
    print(args)

    # setup width and heigth
    rows, columns = popen('stty size', 'r').read().split()
    #  mywidth, myheigth = 27,9
    if args['columns'] == -1: columns = int(columns)
    else: columns = args['columns']
    if args['rows'] == -1: rows = int(rows)
    else: rows = args['rows']

    # setup seed value
    if args['seed'] == -1:
        myseed = 1
        myseed = int( timer() * 1e9 % 2**32 )
    else:
        myseed = args['seed']
    seed(myseed)
    npseed(myseed)

    print(f'python3 sim_waves_main.py -s {myseed} -r {rows} -c {columns}')

    #  run_test_lcs_base(rows=rows, columns=columns)
    #  run_test_lcs_base(rows=4000, columns=4000)
    run_test_lcs_base(rows=20, columns=100)
    #  test_generate_similar_string_nonrepeating()
    #  run_test_lcs_similar()

if __name__ == '__main__':
    main()
