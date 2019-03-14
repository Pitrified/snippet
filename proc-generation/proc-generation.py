from random import randint
from random import choices
from itertools import accumulate
from math import ceil

def pm(mappa, width, heigth):
    for i, c in enumerate(mappa):
        print(c, end='')
        if (i+1) % width == 0: print()

def cell2xy(cella, width, heigth):
    if cella is None: return None, None

    y = cella - (cella % width) 
    x = cella - y
    y = int( y / width )
    return x,y

def xy2cell(x, y, width, heigth):
    return x + y*width

def randomize(mappa, width, heigth, tiles, fraction):
    newmappa = mappa
    #  tot_weights = sum([tiles[x][0] for x in tiles] )
    cumulative_weights = list(accumulate( [tiles[x][0] for x in tiles] ) )
    tiles_letter = [t for t in tiles]
    #  print(tiles_letter, cumulative_weights)

    tot_tiles = width*heigth
    new_tiles = ceil(tot_tiles * fraction)
    #  print(f'tt {tot_tiles} new_tiles {new_tiles}')
    for i in range(new_tiles):
        cella = randint(0, tot_tiles-1)
        y = cella - (cella % width) 
        x = cella - y
        y = int( y / width )
        #  print(f'cella {cella}: ({x}, {y})')

        new_t = choices(tiles_letter, cum_weights=cumulative_weights)[0]
        newmappa[cella] = new_t
        #  pm(newmappa, width, heigth)
        #  print()
    return newmappa

def find_neigh(cella, width, heigth):
    #  y = cella - (cella % width) 
    #  x = cella - y
    #  y = int( y / width )
    x,y = cell2xy(cella, width, heigth)

    #  u = (y-1) * width + x
    #  d = (y+1) * width + x
    #  l = y * width + x-1
    #  r = y * width + x+1
    u = xy2cell(x, y-1, width, heigth)
    d = xy2cell(x, y+1, width, heigth)
    l = xy2cell(x-1, y, width, heigth)
    r = xy2cell(x+1, y, width, heigth)
    #  print(f'{cella} ({x}, {y}): u{u} d{d} l{l} r{r}')

    return u, d, l, r

def evolve(mappa, width, heigth, tiles):
    newmappa = mappa
    tot_tiles = width*heigth
    for cella in range(tot_tiles):
        y = cella - (cella % width) 
        x = cella - y
        y = int( y / width )
        #  print(f'cella {cella}: ({x}, {y})')
        u, d, l, r = find_neigh(cella, width, heigth)
    return newmappa

def test_neigh(mappa, width, heigth):
    newmappa = mappa
    cella = 6
    x, y = cell2xy(cella, width, heigth)
    ritorno = xy2cell(x, y, width, heigth)
    print(f'cella {cella}: ({x}, {y}) -> {ritorno}')
    u, d, l, r = find_neigh(cella, width, heigth)
    print(f'u {u}: {cell2xy(u, width, heigth)}')
    print(f'd {d}: {cell2xy(d, width, heigth)}')
    print(f'l {l}: {cell2xy(l, width, heigth)}')
    print(f'r {r}: {cell2xy(r, width, heigth)}')
    newmappa[cella] = 'x'
    newmappa[u] = 'u'
    newmappa[d] = 'd'
    newmappa[l] = 'l'
    newmappa[r] = 'r'
    pm(newmappa, width, heigth)

def main():
    width = 30
    heigth = 10
    width, heigth = 4,3
    
    mappa = ['e'] * (width*heigth)
    print()
    pm(mappa, width, heigth)
    print()

    tiles = {
            'l' : [1, 0.05],
            't' : [10, 0.1],
            'w' : [5, 0.025],
            }

    fraction = 0.05

    #  print('Randomizzo')
    #  mappa = randomize(mappa, width, heigth, tiles, fraction)
    #  pm(mappa, width, heigth)
    #  print()

    #  print('Evolvo')
    #  num_iter = 1
    #  for i in range(num_iter):
        #  mappa = evolve(mappa, width, heigth, tiles)
        #  pm(mappa, width, heigth)
        #  print()

    test_neigh(mappa, width, heigth)

if __name__ == '__main__':
    main()
