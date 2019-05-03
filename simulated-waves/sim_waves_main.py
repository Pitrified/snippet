import argparse

from timeit import default_timer as timer
from random import seed
from numpy.random import seed as npseed
from os import popen

from sim_waves_holder import Holder

def parse_arguments():
    # setup parser
    parser = argparse.ArgumentParser(
            description='Procedurally generate a map',
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

def test_waves_base(rows, columns):
    '''create water and do things'''
    print(f'doing test_waves_base r {rows} c {columns}')

    bucket = Holder(rows, columns)

    #  depth = 10
    depth = 2
    qty = 20
    bucket.fill_bottom(depth, qty)
    #  bucket.add_drop(row=1, column=4, radius=1, qty=5)
    bucket.add_drop(row=1, column=4, radius=4, qty=5)
    #  bucket.print_qty()
    bucket.print_qty_small()

def main():
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

    test_waves_base(rows=rows, columns=columns)

if __name__ == '__main__':
    main()
