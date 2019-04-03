#  import sys
import argparse
from timeit import default_timer as timer
from random import seed
#  from random import random
#  from random import choices
#  from random import randint
#  from random import randrange
#  from os import system
from os import popen

from proc_gen_class import MapGenerator
from proc_gen_class import Tile

def parse_arguments():
    # setup parser
    parser = argparse.ArgumentParser(
            description='Procedurally generate a map',
            )

    # positional args (mandatory)
    #  parser.add_argument('echo', help='echo this string')

    parser.add_argument('-w', "--width",
            type=int,
            default=-1,
            help="width of the map, -1 or empty for auto")

    parser.add_argument('-e', "--heigth",
            type=int,
            default=-1,
            help="heigth of the map, -1 or empty for auto")

    parser.add_argument('-f', "--fraction",
            type=float,
            default=-1,
            help="fraction of cells to randomize")

    #  parser.add_argument("-v", "--verbose",
            #  action="store_true",                # store only true or false value
            #  help="increase output verbosity")

    parser.add_argument("-m", "--movie",
            action="store_true",                # store only true or false value
            help="visualize the evolution")

    # limit possible values
    #  parser.add_argument('-n', '--number',
            #  type=int,
            #  choices=[0,1,2],
            #  help='number can only be 0,1,2',
            #  )

    # fancy option with count
    #  parser.add_argument('-r', '--repeat',
            #  action='count',
            #  default=0,
            #  help='you can repeat this option and it will be counted',
            #  )

    # last line to parse them
    args = parser.parse_args()

    #  parse the args even more if needed
    args_parsed = { a : v for a, v in args._get_kwargs() }
    return args_parsed

def test_film_run():
    pass

def test_film(width, heigth, tiles, fraction):
    mymap = MapGenerator(width, heigth, tiles, fraction=fraction)
    mymap.film()

def test_comp_perf_run(width, heigth, tiles, fraction):
    mymap = MapGenerator(width, heigth, tiles, fraction)
    t1 = timer()
    mymap.full_evolve()
    t2 = timer()
    mymap.find_components()
    t3 = timer()

    return t2-t1, t3-t2

def test_comp_perf():
    width = 1000
    heigth = 1000
    tiles = {
            'l' : [2, 5, 31],
            'x' : [8, 30, 34],
            'm' : [5, 25, 33],
            }
    fraction = 0.1

    t_evolve, t_find = test_comp_perf_run(width, heigth, tiles, fraction)
    print(f'evolve: {t_evolve:.6f} find: {t_find:.6f}')

def main():
    args = parse_arguments()

    print(args)

    rows, columns = popen('stty size', 'r').read().split()
    #  mywidth, myheigth = 27,9
    if args['width'] == -1: width = int(columns)
    else: width = args['width']
    if args['heigth'] == -1: heigth = int(rows)
    else: heigth = args['heigth']
    #  width, heigth = 60,30
    #  width, heigth = 270,70
    #  width, heigth = 4,3
    #  width, heigth = int(columns), int(rows)

    if args['fraction'] == -1: fraction = 0.08
    else: fraction = args['fraction']

    # tiles: prob di spawnare random
    #        prob di replicarsi
    #        colore
    #  tiles = {
            #  'l' : [2, 5, 31],
            #  'x' : [8, 30, 34],
            #  'm' : [5, 25, 33],
            #  }
    tiles = {
            'l' : Tile(letter='l', prob_spawn=2, prob_repl=5, color=31),
            'x' : Tile(letter='x', prob_spawn=8, prob_repl=30, color=34),
            'm' : Tile(letter='m', prob_spawn=5, prob_repl=25, color=33),
            }

    #  seed = randrange(sys.maxsize)
    myseed = 1
    #  myseed = 5
    myseed = int( timer() * 10000000 )
    #  myseed = 649567331430
    # TODO seed from cli
    #  Random(seed)
    seed(myseed)
    print(f'Seed used: {myseed} fraction {fraction} w {width} e {heigth}')
    # bad seeds
    # good seeds
    # seed 649567331430 f 0.08 w 158 e 87 discard 0.3


    #  mymap = MapGenerator(width, heigth, tiles, fraction=0.03)
    mymap = MapGenerator(width, heigth, tiles, fraction=fraction)

    if args['movie']:
        mymap.film()
    else:
        mymap.full_evolve()
        print(mymap.fast_print())
        #  print(mymap)

    # TODO show components or not from cli
    mymap.find_components()
    print(mymap.print_components())
    #  print(mymap.components)

    #  test_comp_perf()

    path = mymap.find_path(1, 2)
    mymap.print_path(path)

    #  img_name = 'lamappagrande.html'
    #  mymap.map2html(img_name)

if __name__ == '__main__':
    main()

# TODO
# con pygame fai una cosa simile www.redblobgames.com/maps/mapgen4/
# o anche con tkinter: slider cambiano parametri, pulsanti randomize, evolve, film
