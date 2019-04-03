from itertools import accumulate
from itertools import groupby
from math import ceil
from os import system
from os import popen
from random import choices
from random import randint
from random import randrange
#  from random import Random
from random import seed
from time import sleep
from queue import Queue
import sys
import argparse
from timeit import default_timer as timer

class MapGenerator:
    def __init__(self, width, heigth, tiles,
                 empty_char='e',
                 fraction = 0.1,
                 ):
        # obbligatori
        self.width = width
        self.heigth = heigth
        self.tiles = tiles

        # default impostabili dal costruttore
        self.empty_char = empty_char
        self.fraction = fraction

        # default impostabili dopo se vuoi
        self.empty_char_color = 30

        # inizializza
        self.erase()

    def erase(self):
        self.mappa = [self.empty_char] * (self.width*self.heigth)
        self.empty_left = self.width * self.heigth

    def __repr__(self):
        repr_map = self.__str__()
        repr_map += f'empty_char= {self.empty_char}'
        return repr_map
        # print(repr(mymap)) to see this

    def __str__(self):
        str_map = ''
        cs = '\033[{color}m{char}\033[0m'

        for i, c in enumerate(self.mappa):
            if c == self.empty_char:
                color = self.empty_char_color
            else:
                color = self.tiles[c][2]

            str_map += cs.format(color=color, char=c)
            
            if (i+1) % self.width == 0:
                str_map += '\n'
        return str_map
        # print(mymap)

    def fast_print(self):
        str_map = ''
        cs = '\033[{color}m{char}\033[0m'

        for r in range(self.heigth):
            riga = self.mappa[ r*self.width : (r+1)*self.width ]
            str_riga = ''
            for k, g in groupby(riga):
                if k == self.empty_char:
                    color = self.empty_char_color
                else:
                    color = self.tiles[k][2]
                rk = k * len(list(g))
                str_riga += cs.format(color=color, char=rk)
            str_map += str_riga + '\n'
        return str_map

    def cell2xy(self, cella):
        if cella is None: return None, None
        y = cella - (cella % self.width) 
        x = cella - y
        y = int( y / self.width )
        return x,y

    def xy2cell(self, x, y):
        if x is None or y is None:
            return None
        if not 0 <= x < self.width:
            return None
        if not 0 <= y < self.heigth:
            return None
        return x + y*self.width

    def find_neigh(self, cella):
        x,y = self.cell2xy(cella)
        u = self.xy2cell(x, y-1)
        d = self.xy2cell(x, y+1)
        l = self.xy2cell(x-1, y)
        r = self.xy2cell(x+1, y)
        return u, d, l, r

    def randomize(self):
        cum_weights = list(accumulate( [self.tiles[x][0] for x in self.tiles] ) )
        tiles_letter = [t for t in self.tiles]
        tot_tiles = self.width*self.heigth
        new_tiles = ceil(tot_tiles * self.fraction)
        for i in range(new_tiles):
            cella = randint(0, tot_tiles-1)
            if self.mappa[cella] == self.empty_char:
                self.empty_left -= 1

            x,y = self.cell2xy(cella)
            new_t = choices(tiles_letter, cum_weights=cum_weights)[0]
            self.mappa[cella] = new_t

    def evolve(self):
        tot_tiles = self.width*self.heigth
        new_cells = {}

        for cella in range(tot_tiles):
            if self.mappa[cella] != self.empty_char:
                continue

            neigh_cells = self.find_neigh(cella)
            good_neigh_cells = [x for x in neigh_cells if x is not None]
            type_neigh = [self.mappa[x] for x in good_neigh_cells]
            good_type_neigh = [x for x in type_neigh if x != self.empty_char]

            cum_weights = list(accumulate( [self.tiles[x][1] for x in good_type_neigh] ) )

            if len(cum_weights) > 0:
                new_t = choices(good_type_neigh, cum_weights=cum_weights)[0]
                new_cells[cella] = new_t

        for c in new_cells:
            self.mappa[c] = new_cells[c]

        self.empty_left -= len(new_cells)

    def film(self, max_iter=None, erase=True):
        if erase:
            self.erase()
            print(self.__str__())
            sleep(0.5)

        self.randomize()
        print(self.__str__())
        sleep(0.5)

        if max_iter is None:
            max_iter = 25
        for i in range(max_iter):
            self.evolve()
            print(self.__str__())
            sleep(0.5)
            if self.empty_left == 0:
                break

    def map2html(self, full_filename, title=None):
        htmlstring = ''
        htmlstring += '<html>\n'
        htmlstring += '<head>\n'
        htmlstring += '<title>{titolo}</title>\n'
        htmlstring += '</head>\n'
        htmlstring += '<body style="background:#000000">\n'
        htmlstring += '<div style="background:#000000; letter-spacing:3px; font-family: monospace, fixed;">\n'
        htmlstring += '<pre>\n'
        htmlstring += '{immagine}'
        htmlstring += '</pre>\n'
        htmlstring += '</div>\n'
        htmlstring += '</body>\n'
        htmlstring += '</html>\n'

        spanstring = '<span style="color:{color}">{char}</span>'

        if title is None: title = 'A beautiful map'

        html_colors = {
                30 : '2d2d2d',      # grigio
                31 : 'da2323',      # rosso
                34 : '194084',      # blu
                33 : 'ffcc00',      # giallo
                }

        str_map = ''
        for r in range(self.heigth):
            riga = self.mappa[ r*self.width : (r+1)*self.width ]
            str_riga = ''
            for k, g in groupby(riga):
                #  print(k, len(list(g)))
                if k == self.empty_char:
                    color = self.empty_char_color
                else:
                    color = self.tiles[k][2]
                color = html_colors[color]
                rk = k * len(list(g))
                str_riga += spanstring.format(color=color, char=rk)
            str_map += str_riga + '\n'

        html_page = htmlstring.format(titolo=title, immagine=str_map)
        with open(full_filename, 'w') as f:
            f.write(html_page)

    def full_evolve(self, max_iter=None, erase=False):
        if erase:
            self.erase()
            self.randomize()

        if self.empty_left == self.width*self.heigth:
            self.randomize()

        if max_iter is None:
            max_iter = 50

        for i in range(max_iter):
            self.evolve()
            if self.empty_left == 0:
                break

    def find_components(self):
        # componente : [celle, della, comp, ... ]
        # TODO add this way of saving them
        self.components_set = {}
        # lista delle componenti
        self.components = [-1] * (self.width * self.heigth)
        i = 0
        comp = 0
        while i < self.width * self.heigth -1: #print(f'i {i}')
            # se i e' gia' in una componente, saltalo
            if self.components[i] != -1:
                i += 1
                continue

            #  to_process = Queue()
            to_process = [i]
            cur_char = self.mappa[i]
            #  print(f'Analizzo i {i} carattere {cur_char}')
            # TODO might be a set, check performance of pop and in

            all_neigh = self.find_neigh(i)
            all_neigh = [n for n in all_neigh if n is not None]
            # TODO this is silly, just return a list that doesnt include them
            new_neigh = [n for n in all_neigh
                    if self.components[n] == -1   # non devono essere gia' in componenti
                    and n not in to_process       # non deve essere gia' nella coda da processare
                    and self.mappa[n] == cur_char # deve essere del carattere corrispondente
                    ]
            to_process.extend(new_neigh)

            #  proc = i
            #  proc = to_process.pop(0)
            while len(to_process) > 0:
                proc = to_process.pop(0)
                all_neigh = self.find_neigh(proc)
                all_neigh = [n for n in all_neigh if n is not None]
                # TODO this is silly, just return a list that doesnt include them
                new_neigh = [n for n in all_neigh
                        if self.components[n] == -1   # non devono essere gia' in componenti
                        and n not in to_process       # non deve essere gia' nella coda da processare
                        and self.mappa[n] == cur_char # deve essere del carattere corrispondente
                        ]
                to_process.extend(new_neigh)
                #  print(f'proc {proc} an {all_neigh} nn {new_neigh} tp {to_process}')
                #  print(f'proc {proc}')
                self.components[proc] = comp

            comp += 1
            i += 1

    def print_components(self):
        str_map = ''
        #  cs = '\033[{color}m{char:0>2}\033[0m'
        cs = '\033[{color}m{char}\033[0m'

        #  colors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        #  colors = [1, 2, 3, 4, 6, 7, 8, 9, 10]
        colors = [
                30, 31, 32, 33, 34, 35, 36, 37,
                40, 41, 42, 43, 44, 45, 46, 47,
                90, 91, 92, 93, 94, 95, 96, 97,
                100, 101, 102, 103, 104, 105, 106, 107,
                ]
        for r in range(self.heigth):
            riga = self.components[ r*self.width : (r+1)*self.width ]
            str_riga = ''
            for k, g in groupby(riga):
                color = colors[k % len(colors) ]
                #  pad_k = f'{k:0>2}'  # full comp numbers
                pad_k = f'{str(k):0>1.1}' # compact view
                #  pad_k = f'{str(k):1.1}' # compact view
                rk = pad_k * len(list(g))
                str_riga += cs.format(color=color, char=rk)
            str_map += str_riga + '\n'
        return str_map

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
            help="width of the map")

    parser.add_argument('-e', "--heigth",
            type=int,
            default=-1,
            help="heigth of the map")

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
    width = 10#00
    heigth = 10#00
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
    tiles = {
            'l' : [2, 5, 31],
            'x' : [8, 30, 34],
            'm' : [5, 25, 33],
            }

    #  seed = randrange(sys.maxsize)
    myseed = 1
    myseed = int( timer() * 10000000 )
    #  Random(seed)
    seed(myseed)
    print(f'Seed used: {myseed}')
    # bad seeds
    # h 50 w 20 seed 4801403895470927478 f 0.03

    #  mymap = MapGenerator(width, heigth, tiles, fraction=0.03)
    mymap = MapGenerator(width, heigth, tiles, fraction=fraction)

    if args['movie']:
        mymap.film()
    else:
        mymap.full_evolve()
        print(mymap.fast_print())
        #  print(mymap)

    mymap.find_components()
    print(mymap.print_components())

    #  print(mymap.components)

    #  test_comp_perf()

    #  img_name = 'lamappagrande.html'
    #  mymap.map2html(img_name)

if __name__ == '__main__':
    main()

### TODO ###
# self.empty_cells = numero di celle ancora vuote
#     evolve e randomize aggiornano il conteggio
# mini dizionario per i colori piu` sani
# i parametri passati da argv
# print to HTML and markdown, ottimizza lettere simili in fila
# ottimizza anche stringa da stampare
# anche se i vicini sono popolati puo' a volte restare vuota
# edge detection
#     union set - trova molestamente le componenti
#     con gradiente?
