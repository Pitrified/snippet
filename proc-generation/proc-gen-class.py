from random import randint
from random import choices
from itertools import accumulate
from math import ceil
from os import system

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
        self.mappa = [self.empty_char] * (self.width*self.heigth)

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

def main():
    width, heigth = 27,9
    #  width, heigth = 4,3

    # tiles: prob di spawnare random
    #        prob di replicarsi
    #        colore
    tiles = {
            'l' : [2, 5, 31],
            'x' : [8, 30, 34],
            'm' : [5, 25, 33],
            }
    mymap = MapGenerator(width, heigth, tiles)

    print(mymap)

    mymap.randomize()
    print(mymap)

    max_iter = 4
    for i in range(max_iter):
        mymap.evolve()
        print(mymap)

if __name__ == '__main__':
    main()

### TODO ###
# self.empty_cells = numero di celle ancora vuote
#     evolve e randomize aggiornano il conteggio
# mini dizionario per i colori piu` sani
