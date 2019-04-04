#!/usr/bin/env python
#stackoverflow.com/questions/15682537/ansi-color-specific-rgb-sequence-bash
#gist.github.com/XVilka/8346728#now-supporting-truecolor

from colorsys import hsv_to_rgb
from math import ceil 
from math import floor 
from math import pi
from math import sin
from os import popen
from sys import maxsize
from time import sleep

class Waver:
    def __init__(self, width, heigth, 
            function,
            base_char='o',
            ):
        self.width = width
        self.heigth = heigth
        self.function = function
        self.base_char = base_char

        self.hue = 40

        self.find_extremes()

    def find_extremes(self):
        '''brute force your way to find the min and max
        sadly you can't do this for all time'''
        self.func_min = maxsize
        self.func_max = - maxsize
        max_t = 1000
        for x in range(self.width):
            for y in range(self.heigth):
                for t in range(max_t):
                    val = self.evaluate(x, y, t)
                    if val < self.func_min:
                        self.func_min = floor(val)
                    if val > self.func_max:
                        self.func_max = ceil(val)
        print(f'min {self.func_min} max {self.func_max}')

    def evaluate(self, x, y, t):
        # XXX this is possibly the most useless function call ever
        return self.function(x, y, t)

    def print_at_color(self, t):
        #  form_char = '\x1b[38;2;{};{};{}m{:02d}'
        form_char = '\x1b[38;2;{};{};{}m{:0>2}'
        #  form_char = '\x1b[38;2;{};{};{}m{:02.0f}'
        evstr = ''
        for i in range(self.width):
            for j in range(self.heigth):
                val = self.evaluate(i, j, t) 
                #  val = str(self.evaluate(i, j, t) )
                r, g, b = self.evaluate_rgb(val)
                i_val = int(val)
                f_val = f'{i_val:03d}'[-2:]
                evstr += form_char.format(r, g, b, f_val)
            evstr += '\n'
        return evstr

    def evaluate_rgb(self, val):
        '''evaluate the function and map the result to the 
        corresponding color, as defined by hue,
        and using func_max e func_min,
        by changing the saturation'''
        value = 1
        if val > self.func_max:
            print(f'val {val} sopra il massimo {self.func_max}')
            val = self.func_max # XXX forse -1 lol
        if val < self.func_min:
            print(f'val {val} sotto il minimo {self.func_min}')
            val = self.func_min
        saturation = (val-self.func_min) / (self.func_max-self.func_min)
        r, g, b = hsv_to_rgb(self.hue, saturation, value)
        r = floor(r * 255)
        g = floor(g * 255)
        b = floor(b * 255)
        #  print(f'val {val} r {r} g {g} b {b}')
        return r, g, b

    def print_at(self, t):
        #  form_char = '{:0>3}'
        form_char = '{:_>3}'
        evstr = ''
        for i in range(self.width):
            for j in range(self.heigth):
                val = str(self.evaluate(i, j, t) )
                evstr += form_char.format(val)
            evstr += '\n'
        return evstr

    def rgb2str(self, r, g, b):
        #  return f'\x1b[38;2;{r};{g};{b}m{{}}\x1b[0m'
        return f'\x1b[38;2;{r};{g};{b}m{{}}'

    def format_rgb(self, string, r, g, b):
        return f'\x1b[38;2;{r};{g};{b}m{string}'

def myfunc(x, y, t):
    #  return x+y+ (t%5)
    #  return x+y+ sin(t * pi / 12)
    #  return 20* sin(x+y+ t * pi / 12)
    return 20 * sin(x/4+y/4+ t * pi / 12) + 5 * sin(x/4+y/4+ t * pi / 6)

def test_print():
    width, heigth  = 10, 10
    #  width, heigth  = 3, 3
    rows, columns = popen('stty size', 'r').read().split()
    width = int(columns)
    heigth = int( int(rows) / 3)
    base_char = 'o'
    waving = Waver(width, heigth, myfunc, base_char)

    #  rgbs = rgb2str(23, 234, 56) 
    #  print(rgbs.format('wawawa') )
    #  print(format_rgb('wowowo', 23, 234, 56) )

    #  print(waving.evaluate(1,2,3) )
    #  print(waving.print_at(4) )

    for t in range(100):
        #  print(waving.print_at(t) )
        sleep(0.1)
        print(waving.print_at_color(t))


def main():
    test_print()

if __name__ == '__main__':
    main()
