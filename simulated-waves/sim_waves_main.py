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

    parser.add_argument('-i', "--num_iter",
            type=int,
            default=-1,
            help="evolve iteration to do")

    # last line to parse them
    args = parser.parse_args()

    #  parse the args even more if needed
    #  args_parsed = { a : v for a, v in args._get_kwargs() }
    #  return args_parsed
    return args

def do_evolve(bucket, num):
    #  char_wid = 2
    for _ in range(num):
        #  bucket.evolve()
        str_evolve_debug = bucket.evolve_steps()

        #  print(f'{str_evolve_debug}')

        print(f'{bucket.get_str_sum_info()}')

        #  print(f'{bucket.get_str_qty_small_saturated(1)}')
        print(f'{bucket.get_str_qty_small_saturated(6)}')

        #  print(f'{bucket.get_str_recap(3)}')
        #  print(f'{bucket.get_str_recap_sat(3)}')

def do_evolve_wait(bucket, num):
    #  char_wid = 2
    for _ in range(num):
        #  bucket.evolve()
        str_evolve_debug = bucket.evolve_steps()

        #  print(f'{str_evolve_debug}')

        print(f'{bucket.get_str_sum_info()}')

        print(f'{bucket.get_str_qty_small_saturated(2)}')
        #  print(f'{bucket.get_str_qty_small_saturated(6)}')

        #  print(f'{bucket.get_str_recap(3)}')
        #  print(f'{bucket.get_str_recap_sat(3)}')

def test_waves_mini(num_iter):
    rows = 3
    columns = 5
    print(f'doing test_waves_mini r {rows} c {columns} ni {num_iter}')
    bucket = Holder(rows, columns)

    depth = 1
    qty = 20
    bucket.fill_bottom(depth, qty)
    bucket.add_drop(row=0, column=3, radius=0, qty=5)
    print(f'{bucket.get_str_qty_small_saturated(3)}')

    do_evolve(bucket, num_iter)

def test_waves_base(rows, columns, num_iter):
    '''create water and do things'''
    print(f'doing test_waves_base r {rows} c {columns} ni {num_iter}')

    bucket = Holder(rows, columns)

    #  depth = 10
    depth = 2
    qty = 20
    #  qty = 200
    bucket.fill_bottom(depth, qty)
    bucket.add_drop(row=1, column=4, radius=1, qty=5)
    #  bucket.add_drop(row=1, column=4, radius=4, qty=5)
    #  bucket.add_drop(row=2, column=15, radius=12, qty=2)

    #  bucket.print_qty()
    #  print(f'{bucket.get_str_qty_small()}')
    #  print(f'{bucket.get_str_qty_small(3)}')
    print(f'Starting state:')
    print(f'{bucket.get_str_qty_small_saturated(3)}')

    #  do_evolve(bucket, 3)
    do_evolve(bucket, num_iter)

def test_waves_big(rows, columns, num_iter):
    '''create water and do things'''
    print(f'doing test_waves_big r {rows} c {columns} ni {num_iter}')

    bucket = Holder(rows, columns, max_capacity=50)

    depth = 7
    qty = 20
    #  qty = 200
    bucket.fill_bottom(depth, qty)
    bucket.fill_bottom(depth=5, qty=20)
    bucket.add_drop(row=1, column=4, radius=1, qty=5)
    bucket.add_drop(row=1, column=4, radius=4, qty=5)
    bucket.add_drop(row=2, column=15, radius=12, qty=2)

    print(f'Starting state:')
    print(f'{bucket.get_str_sum_info()}')
    print(f'{bucket.get_str_qty_small_saturated(1)}')

    do_evolve_wait(bucket, num_iter)

def main():
    args = parse_arguments()
    print(args)

    # setup width and heigth
    rows, columns = popen('stty size', 'r').read().split()
    #  mywidth, myheigth = 27,9
    if args.columns == -1: columns = int(columns)
    else: columns = args.columns
    if args.rows == -1: rows = int(rows)
    else: rows = args.rows
    if args.num_iter == -1: num_iter = 3
    else: num_iter = args.num_iter

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int( timer() * 1e9 % 2**32 )
    else:
        myseed = args.seed
    seed(myseed)
    npseed(myseed)

    print(f'python3 sim_waves_main.py -s {myseed} -r {rows} -c {columns} -i {num_iter}')

    #  test_waves_base(rows=rows, columns=columns, num_iter=num_iter)
    test_waves_big(rows=rows, columns=columns, num_iter=num_iter)
    #  test_waves_mini(num_iter)

if __name__ == '__main__':
    main()
