from copy import deepcopy
from random import randint
from random import choices
from itertools import accumulate
from math import ceil
from collections import Counter
from os import system

def pm(mappa, width, heigth):
    for i, c in enumerate(mappa):
        print(c, end='')
        if (i+1) % width == 0: print()

def out(color, char):
    #  system("tput setab " + str(color) + "; echo -n " + ("\"% 0s\"" % char))
    #  system("tput setab " + str(color) + "; echo -n " + ('"% 0s"' % char))
    #  system("tput sgr0")
    #  s = f'tput setab {color}; echo -n "{char}"; tput sgr 0 0'

    #  s = f'tput setaf {color}; echo -n "{char}"; tput sgr 0 0'
    #  s = f'echo -n "\\033[{color+30}m{char}\\033[0m"'
    # martin-thoma.com/colorize-your-scripts-output/
    # this is a LOT faster
    # mewbies.com/motd_console_codes_color_chart_in_color_black_background.htm
    #  system(s)
    print(f"\033[{color+30}m{char}\033[0m", end='')

def pmc(mappa, width, heigth, tiles):
    for i, c in enumerate(mappa):
        color = 0 if c == 'e' else tiles[c][2]
        out(color, c)
        if (i+1) % width == 0: print()

def cell2xy(cella, width, heigth):
    if cella is None: return None, None
    y = cella - (cella % width) 
    x = cella - y
    y = int( y / width )
    return x,y

def xy2cell(x, y, width, heigth):
    if x is None or y is None or (not 0 <= x < width) or (not 0 <= y < heigth):
        return None
    return x + y*width

def find_neigh(cella, width, heigth):
    x,y = cell2xy(cella, width, heigth)
    u = xy2cell(x, y-1, width, heigth)
    d = xy2cell(x, y+1, width, heigth)
    l = xy2cell(x-1, y, width, heigth)
    r = xy2cell(x+1, y, width, heigth)
    return u, d, l, r

def test_neigh(mappa, width, heigth, cella):
    newmappa = deepcopy(mappa)
    #  cella = 6
    x, y = cell2xy(cella, width, heigth)
    ritorno = xy2cell(x, y, width, heigth)
    print(f'cella {cella}: ({x}, {y}) -> {ritorno}')
    u, d, l, r = find_neigh(cella, width, heigth)
    print(f'u {u}: {cell2xy(u, width, heigth)}')
    print(f'd {d}: {cell2xy(d, width, heigth)}')
    print(f'l {l}: {cell2xy(l, width, heigth)}')
    print(f'r {r}: {cell2xy(r, width, heigth)}')
    newmappa[cella] = 'x'
    if u is not None: newmappa[u] = 'u'
    if d is not None: newmappa[d] = 'd'
    if l is not None: newmappa[l] = 'l'
    if r is not None: newmappa[r] = 'r'
    pm(newmappa, width, heigth)

def run_tests_neigh(mappa, width, heigth):
    celle = [6, 0, width*heigth-1, width, width-1, width+1, heigth, heigth-1, heigth+1]
    for cella in celle:
        test_neigh(mappa, width, heigth, cella)
        print()

def randomize(mappa, width, heigth, tiles, fraction):
    cumulative_weights = list(accumulate( [tiles[x][0] for x in tiles] ) )
    tiles_letter = [t for t in tiles]
    tot_tiles = width*heigth
    new_tiles = ceil(tot_tiles * fraction)
    for i in range(new_tiles):
        cella = randint(0, tot_tiles-1)
        x,y = cell2xy(cella, width, heigth)
        new_t = choices(tiles_letter, cum_weights=cumulative_weights)[0]
        mappa[cella] = new_t

def evolve(mappa, width, heigth, tiles):
    tot_tiles = width*heigth
    #  mp = mappa
    new_cells = {}
    for cella in range(tot_tiles):
        if not mappa[cella] == 'e':
            continue
        #  x, y = cell2xy(cella, width, heigth)
        u, d, l, r = find_neigh(cella, width, heigth)
        #  all_neigh = [x for x in [mp[u], mp[d], mp[l], mp[r]] if x is not None]
        all_neigh = [x for x in [u, d, l, r] if x is not None]
        #  print(f'numero celle vicini {all_neigh}')
        type_neigh = [mappa[x] for x in all_neigh if mappa[x] is not 'e']
        #  print(f'tipo celle vicini {type_neigh}')
        cumulative_weights = list(accumulate( [tiles[x][1] for x in type_neigh] ) )
        #  tiles_letter = [t for t in tiles]
        #  new_t = choices(tiles_letter, cum_weights=cumulative_weights)[0]
        if len(cumulative_weights) > 0:
            new_t = choices(type_neigh, cum_weights=cumulative_weights)[0]
            #  print(f'an {all_neigh} cw {cumulative_weights} tl {tiles_letter} new_t {new_t}')
            #  mappa[cella] = new_t#.upper()
            new_cells[cella] = new_t

    for c in new_cells:
        mappa[c] = new_cells[c]

def main():
    width = 30
    heigth = 10
    width, heigth = 4,3
    width, heigth = 27,9
    #  width, heigth = 60, 50
    
    mappa = ['e'] * (width*heigth)
    print()
    pm(mappa, width, heigth)
    print()

    tiles = {
            #  'l' : [1, 5, 1],
            'l' : [2, 5, 1],
            'x' : [8, 30, 4],
            'm' : [5, 25, 3],
            }

    fraction = 0.15

    #  run_tests_neigh(mappa, width, heigth)

    print('Randomizzo')
    randomize(mappa, width, heigth, tiles, fraction)
    pmc(mappa, width, heigth, tiles)
    #  pm(mappa, width, heigth)
    print()

    #  print(Counter(mappa))

    print('Evolvo')
    num_iter = 4
    for i in range(num_iter):
        print(f'Round {i+1}')
        evolve(mappa, width, heigth, tiles)
        #  pm(mappa, width, heigth)
        pmc(mappa, width, heigth, tiles)
        print()

    #  pmc(mappa, width, heigth, tiles)


if __name__ == '__main__':
    main()

# TODO
