from itertools import accumulate
from itertools import groupby
from math import ceil
from math import floor 
from colorsys import hsv_to_rgb
#  from os import system
#  from os import popen
from random import choices
from random import randint
#  from random import randrange
#  from random import Random
from random import random
#  from random import seed
from time import sleep
#  from queue import Queue
from collections import deque

class Tile:
    def __init__(self, letter,
            prob_spawn=5,
            prob_repl=5,
            color=33,
            hue=4/6,
            travel_cost=5,
            is_traversable=True,
            ):
        self.letter = letter
        self.prob_spawn = prob_spawn
        self.prob_repl = prob_repl
        self.color = color
        self.hue = hue
        self.travel_cost = travel_cost
        self.is_traversable = is_traversable

class MapGenerator:
    def __init__(self, width, heigth, tiles,
             empty_char='e',
             fraction = 0.1,
             #  discard = 0.5,
             discard = 0.3,
             ):
        # obbligatori
        self.width = width
        self.heigth = heigth
        self.tiles = tiles

        # default impostabili dal costruttore
        self.empty_char = empty_char
        self.fraction = fraction
        self.discard = discard

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
                #  color = self.tiles[c][2]
                color = self.tiles[c].color

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
                    #  color = self.tiles[k][2]
                    color = self.tiles[k].color
                rk = k * len(list(g))
                str_riga += cs.format(color=color, char=rk)
            str_map += str_riga + '\n'
        return str_map

    def hstack_string(self, a, b):
        '''print a and b side by side'''
        sa = a.split('\n')
        sb = b.split('\n')
        
        if len(sa) != len(sb):
            return 'different number of rows my dude'

        hstacked = ''
        for ri in range(len(sa)):
            hstacked += sa[ri]
            hstacked += ' '
            hstacked += sb[ri]
            hstacked += '\n'

        return hstacked

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

    def find_neigh(self, cella, return_none=False):
        x,y = self.cell2xy(cella)
        u = self.xy2cell(x, y-1)
        d = self.xy2cell(x, y+1)
        l = self.xy2cell(x-1, y)
        r = self.xy2cell(x+1, y)
        if return_none:
            return u, d, l, r
        else:
            return (n for n in (u, d, l, r) if n is not None)

    def randomize(self):
        #  cum_weights = list(accumulate( [self.tiles[x][0] for x in self.tiles] ) )
        cum_weights = list(accumulate( [self.tiles[x].prob_spawn for x in self.tiles] ) )
        #  cum_weights = list(accumulate( [ x.prob_spawn for x in self.tiles] ) )
        #  tiles_letter = [t for t in self.tiles]
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
            if random() < self.discard: # only assign this some of the times
                continue

            neigh_cells = self.find_neigh(cella)
            type_neigh = [self.mappa[x] for x in neigh_cells]
            good_type_neigh = [x for x in type_neigh if x != self.empty_char]

            #  cum_weights = list(accumulate( [self.tiles[x][1] for x in good_type_neigh] ) )
            cum_weights = list(accumulate([self.tiles[x].prob_repl for x in good_type_neigh]) )
            #  cum_weights = list(accumulate( [ x.prob_repl for x in good_type_neigh] ) )

            if len(cum_weights) > 0:
                #  print(f'gtn {good_type_neigh} cw {cum_weights}')
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
            max_iter = 250
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
                    #  color = self.tiles[k][2]
                    color = self.tiles[k].color
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
            max_iter = 5000

        for i in range(max_iter):
            self.evolve()
            if self.empty_left == 0:
                break

    def find_components(self):
        # componente : [celle, della, comp, ... ]
        # TODO add this way of saving them
        self.components_dict = {}
        # lista delle componenti
        self.components = [-1] * (self.width * self.heigth)
        i = 0
        comp = 0
        while i < self.width * self.heigth -1: #print(f'i {i}')
            # se i e' gia' in una componente, saltalo
            if self.components[i] != -1:
                i += 1
                continue

            # might be a set, TODO check performance of pop and in
            # even better a collections.deque
            #  to_process = Queue()
            #  to_process = [i]
            to_process = deque( (i,) )
            cur_char = self.mappa[i]
            #  print(f'Analizzo i {i} carattere {cur_char}')

            while len(to_process) > 0:
                #  proc = to_process.pop(0)
                proc = to_process.popleft() # cella da processare
                all_neigh = self.find_neigh(proc)
                new_neigh = (n for n in all_neigh     # i vicini trovati
                        if self.components[n] == -1   # non devono essere gia' in componenti
                        and n not in to_process       # non deve essere gia' nella coda da processare
                        and self.mappa[n] == cur_char # deve essere del carattere corrispondente
                        )
                to_process.extend(new_neigh)          # aggiungili alla coda da processare
                #  print(f'proc {proc} an {all_neigh} nn {new_neigh} tp {to_process}')

                self.components[proc] = comp
                if comp in self.components_dict:
                    self.components_dict[comp].append(proc)
                else:
                    self.components_dict[comp] = [proc]

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
                #  pad_k = f'{str(k):0>1.1}' # compact view
                pad_k = f'{str(k)[-1:]}' # compact view
                #  pad_k = f'{str(k):1.1}' # compact view
                rk = pad_k * len(list(g))
                str_riga += cs.format(color=color, char=rk)
            str_map += str_riga + '\n'
        return str_map

    def print_depth_basic(self):
        str_depth = ''
        for i, c in enumerate(self.depth):
            #  str_depth += f'{str(c)[-1:]}'
            str_depth += f'{str(c)[-2:]: >2}'
            
            if (i+1) % self.width == 0:
                str_depth += '\n'
        return str_depth

    def print_depth_basic_color(self):
        cs = '\033[{color}m{char}\033[0m'
        colors = [
                30, 31, 32, 33, 34, 35, 36, 37,
                40, 41, 42, 43, 44, 45, 46, 47,
                90, 91, 92, 93, 94, 95, 96, 97,
                100, 101, 102, 103, 104, 105, 106, 107,
                ]

        str_depth = ''
        for i, c in enumerate(self.depth):
            #  str_depth += f'{str(c)[-1:]}'
            #  str_depth += f'{str(c)[-2:]: >2}'
            #  f_c = f'{str(c)[-2:]: >2}'
            f_c = f'{str(c)[-2:]:_>2}'
            comp = self.components[i]
            col = colors[comp % len(colors)]
            str_depth += cs.format(color=col, char=f_c)
            
            if (i+1) % self.width == 0:
                str_depth += '\n'

        return str_depth

    def evaluate_rgb_depth(self, z, d_min, d_max, cell):
    #  def evaluate_rgb_depth(self, z, cell):
        cell_type = self.mappa[cell]

        cell_hue = self.tiles[cell_type].hue
        #  print(cell_type)
        #  hue = 4/6 # somewhat decent blue
        hue = cell_hue

        frac = 0.4
        if d_max == d_min:
            saturation = frac
        else:
            saturation = (z-d_min) / (d_max-d_min)
            saturation = saturation * (1-frac) + frac

        value = 1

        r, g, b = hsv_to_rgb(hue, saturation, value)
        r = floor(r * 255)
        g = floor(g * 255)
        b = floor(b * 255)

        #  print(f'val {z:2d} d_min {d_min:4d} d_max {d_max:4d} sat {saturation}')
        #  form_char = '\x1b[38;2;{};{};{}m{:_>2}\033[0m'
        #  f_c = f'{str(z)[-2:]}'
        #  print(f'val {z} r {r:4d} g {g:4d} b {b:4d} : {form_char.format(r, g, b, f_c)}')
        return r, g, b

    def print_depth_rgb(self):
        cs = '\033[{color}m{char}\033[0m'
        form_char = '\x1b[38;2;{};{};{}m{:_>2}'
        #  form_char = '\x1b[38;2;{};{};{}m{}'

        #  d_min = min(self.depth)
        #  d_max = max(self.depth)
        d_min = {}
        d_max = {}
        #  d_min = []
        #  d_max = []
        #  for cell_type in self.tiles:

        # per ogni componente trovo il minimo e massimo
        for comp in self.components_dict:
            depths = [self.depth[c] for c in self.components_dict[comp] ]
            d_min[comp] = min(depths)
            d_max[comp] = max(depths)

        str_depth = ''
        for i, c in enumerate(self.depth):
            comp = self.components[i]
            #  print(f'cell {i:3d} in component {comp} has depth {c}')
            r, g, b = self.evaluate_rgb_depth(c, d_min[comp], d_max[comp], i)
            #  r, g, b = self.evaluate_rgb_depth(c, i)
            #  str_depth += f'{str(c)[-1:]}'
            #  f_c = f'{str(c)[-1:]}'
            f_c = f'{str(c)[-2:]}'
            str_depth += form_char.format(r, g, b, f_c)
            
            if (i+1) % self.width == 0:
                str_depth += '\n'

        return str_depth

    def calc_depth(self):
        '''find the distance to the border of a component'''
        # NOTE if only one component exists, the depth is undefined
        # find cells on the border, put them in to_process
        # linear scan, find_neigh and check for which components
        # go around to_process, distance is 1+ min dist of neigh_cells
        #  self.depth = [-1] * (self.width * self.heigth)
        self.depth = ['e'] * (self.width * self.heigth)
        for comp in self.components_dict:
            #  print(f'doing comp {comp}')
            to_process = deque()
            for cell in self.components_dict[comp]:
                #  print(f'in cell {cell}')
                all_neigh = self.find_neigh(cell)
                for n in all_neigh:                 # if a neigh
                                                    # is in a different component
                                                    # and is not in to_process already
                    if self.components[n] != comp and n not in to_process:
                        to_process.append(cell)     # the cell is on the border
                        self.depth[cell] = 1
                        break

            #  print(self.print_depth_basic_color())

            # to_process now contains the border
            #  print(to_process)
            while len(to_process) > 0:
                proc = to_process.popleft()
                #  print(f'proc {proc}')
                all_neigh = self.find_neigh(proc)
                neigh_cells = (n for n in all_neigh # if a neigh
                    if self.depth[n] == 'e'         # is empty
                    and self.components[n] == comp) # and is in the same component
                # here you could check wether n has different depth near him
                # and the min depth is NOT the one in proc TODO
                for n in neigh_cells:
                    self.depth[n] = self.depth[proc] + 1
                    to_process.append(n)

            # tutto sbagliato
            # iteri su quelli che hanno GIA' depth definita
            # e definisci quella dei vicini
            # va fatto in modo astuto per trovare quella minima
            # devi distinguere tra celle nuove e vecchie
            # anche se forse sono sempre uguali, BOH
            #  all_neigh = self.find_neigh(proc)
            #  neigh_depth = tuple(self.depth[n] for n in all_neigh
                #  if self.components[n] == comp   # in the same comp
                #  and self.depth[n] != 'e')       # depth defined for that neigh
            #  print(f'neigh_depth {neigh_depth}')
            #  if len(neigh_depth) > 0 and self.depth[proc] == 'e':
                #  # if at least a neigh has depth defined
                #  # and the cell has depth undefined
                #  print(f'aggiorno depth di {cell} a {min(neigh_depth)+1}')
                #  self.depth[proc] = min(neigh_depth) + 1
                #  to_process.append(proc)

    def find_path(self, ce_start, ce_end):
        '''Use A* to find best path
        water costs more than land'''
        # basic A* implementation
        # open: squares that are being considered to find the path
        # closed: already considered, don't add again
        # G: cost from start to current square
        # H: estimated cost from current square to end
        # F = G + H
        # get S from open list with lowest score
        # remove S from open and put it in closed
        # for each neighbour T reachable from S
        #   if T in closed: ignore it
        #   if T NOT in open: add it and compute score
        #   if T in open: check if new path has lower score

    def print_path(self, path):
        '''Print map overlay the path'''
        # TODO might be multiple paths
        # should take as input a map as list of char
        # a standard color as list of color as long as the map
        # overrides as dict of {cell : (char, color)}

### TODO ###
# salva i parametri in un file, opzione per ripeterli
# rifare l'intera baracca con numpy e gli array seri?
# poi viene salvata solo la lettera nella stringa
# mini dizionario per i colori piu` sani # in Tile
# edge detection
#     union set - trova molestamente le componenti
#     con gradiente?

### DONE ###
# classe tile piu' astuta, campi seri sono necessari
# componenti trovate con blob tempo lineare
# self.empty_cells = numero di celle ancora vuote
#     evolve e randomize aggiornano il conteggio
# i parametri passati da argv
# print to HTML and markdown, ottimizza lettere simili in fila
# ottimizza anche stringa da stampare
# anche se i vicini sono popolati puo' a volte restare vuota
