#!/usr/bin/env python
#stackoverflow.com/questions/15682537/ansi-color-specific-rgb-sequence-bash
#gist.github.com/XVilka/8346728#now-supporting-truecolor

from colorsys import hsv_to_rgb
from math import ceil 
from math import floor 
from math import pi
from math import sin
from math import sqrt
from os import popen
from sys import maxsize
from time import sleep
from numpy import arctan2

class Waver:
    def __init__(self, width, heigth, 
            function,
            base_char='o',
            ):
        self.width = width
        self.heigth = heigth
        self.function = function
        self.base_char = base_char

        #  self.hue = 0 # red
        #  self.hue = 1/6 # pale yellow
        #  self.hue = 2/6 # this is a green that will kill your eyes
        #  self.hue = 0.5 # light blue
        self.hue = 4/6 # somewhat decent blue
        #  self.hue = 5/6 # fuschkija

        self.find_extremes()

    def find_extremes(self):
        '''brute force your way to find the min and max
        sadly you can't do this for all time'''
        self.func_min = maxsize
        self.func_max = - maxsize
        # might be better to random sample a larger interval?
        # depends on the function I'd say
        #  max_t = 1000
        max_t = 100
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
        # yeah I think this are swapped somewhere
        x_t = self.heigth // 2
        y_t = self.width // 2
        return self.function(x, y, t, x_t, y_t)
        #  return self.function(x, y, t)

    def print_at_color(self, t):
        #  form_char = '\x1b[38;2;{};{};{}m{:02d}'
        form_char = '\x1b[38;2;{};{};{}m{:0>2}'
        #  form_char = '\x1b[38;2;{};{};{}m{:0>1}'
        #  form_char = '\x1b[38;2;{};{};{}m{:02.0f}'
        evstr = ''
        for i in range(self.heigth):
            for j in range(self.width):
                val = self.evaluate(i, j, t) 
                r, g, b = self.evaluate_rgb(val)
                i_val = int(val)
                f_val = f'{i_val:03d}'[-2:] # remove the minus
                evstr += form_char.format(r, g, b, f_val)
            evstr += '\n'
        return evstr

    def evaluate_rgb(self, val):
        '''evaluate the function and map the result to the 
        corresponding color, as defined by hue,
        and using func_max e func_min,
        by changing the saturation'''
        value = 1
        #  value = 0.5
        if val > self.func_max:
            #  print(f'val {val} sopra il massimo {self.func_max}')
            val = self.func_max # XXX forse -1 lol
        if val < self.func_min:
            #  print(f'val {val} sotto il minimo {self.func_min}')
            val = self.func_min
        saturation = (val-self.func_min) / (self.func_max-self.func_min)
        #  saturation = 0
        #  saturation = 1
        #  hue = (val-self.func_min) / (self.func_max-self.func_min)
        #  value = (val-self.func_min) / (self.func_max-self.func_min)
        r, g, b = hsv_to_rgb(self.hue, saturation, value)
        #  r, g, b = hsv_to_rgb(hue, saturation, value)
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

def sinc(x):
    if x == 0:
        return 1
    else:
        return sin(x) / x
        #  return sin(pi* x) / (pi*x) # normalize it if you want

def myfunc(x, y, t, x_t=0, y_t=0):
    # translate
    x = x - x_t
    y = y - y_t
    # polarize
    rho = sqrt( x**2 + y**2 )
    theta = arctan2(x, y)

    #  return x+y+ (t%5)
    #  return x+y+ sin(t * pi / 12)
    #  return 20* sin(x+y+ t * pi / 12)
    #  return 20 * sin(x/4+y/4+ t * pi / 12) + 5 * sin(x/4+y/4+ t * pi / 6)
    #  return 10 * sin( rho - t * pi / 12 ) * sin (t* theta * 4) # cool
    #  return 10 * sin( rho/3 - t * pi / 12 ) * sin ( rho/8 - t * pi / 8 ) # decent waves
    return 10 * sin( rho/3 - t * pi / 12 ) * sin ( rho/8 - t * pi / 8 ) # decent waves !!!
    #  return 10 * sin( - rho * t * pi / 12 ) # weird effects
    #  return 10 * sin(t * pi / 16) * sinc(0.4 * (x-30) ) * sinc(0.4 * (y-30) ) # translated
    #  return 70 * sin(t * pi / 16) * sinc(0.4 * (x-30) ) * sinc(0.4 * (y-30) ) # nice sinc
    #  return 70 * sin(t * pi / 16) * sinc(0.4 * x)  * sinc(0.4 * y)  # nice sinc

def test_print():
    width, heigth  = 10, 10
    #  width, heigth  = 3, 3
    rows, columns = popen('stty size', 'r').read().split()
    width = int(columns) // 2
    heigth = int(rows) - 3
    base_char = 'o'
    waving = Waver(width, heigth, myfunc, base_char)

    #  rgbs = rgb2str(23, 234, 56) 
    #  print(rgbs.format('wawawa') )
    #  print(format_rgb('wowowo', 23, 234, 56) )

    #  print(waving.evaluate(1,2,3) )
    #  print(waving.print_at(4) )

    #  print(waving.print_at(t) )
    for t in range(100):
        sleep(0.1)
        print(waving.print_at_color(t))

    #  print(waving.print_at_color(1))
    #  print(f'rows {rows} cols {columns} width {width}')

def main():
    test_print()

if __name__ == '__main__':
    main()
