from itertools import accumulate
from itertools import groupby
from math import ceil
from os import system
from os import popen
from random import choices
from random import randint
from time import sleep
import argparse

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

def main():
    #  parser = argparse.ArgumentParser()
    #  parser.add_argument('--fill', help='Genera una mappa grande come l\'intero terminale')

    #  if parser.fill:
        #  print('Riempio il terminale')

    width, heigth = 27,9
    width, heigth = 60,30
    #  width, heigth = 270,70
    #  width, heigth = 4,3
    rows, columns = popen('stty size', 'r').read().split()
    width, heigth = int(columns), int(rows)

    # tiles: prob di spawnare random
    #        prob di replicarsi
    #        colore
    tiles = {
            'l' : [2, 5, 31],
            'x' : [8, 30, 34],
            'm' : [5, 25, 33],
            }
    #  mymap = MapGenerator(width, heigth, tiles, fraction=0.03)
    mymap = MapGenerator(width, heigth, tiles, fraction=0.008)

    mymap.film()
    #  mymap.full_evolve()
    #  print(mymap)

    img_name = 'lamappagrande.html'
    #  mymap.map2html(img_name)

if __name__ == '__main__':
    main()

### TODO ###
# self.empty_cells = numero di celle ancora vuote
#     evolve e randomize aggiornano il conteggio
# mini dizionario per i colori piu` sani
# i parametri passati da argv
# print to HTML and markdown, ottimizza lettere simili in fila
