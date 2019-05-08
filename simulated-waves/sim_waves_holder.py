import numpy as np
from colorsys import hsv_to_rgb
from math import floor

class Holder:
    def __init__(self,
            rows,
            columns,
            gravity=10,
            #  max_capacity=100,
            max_capacity=30,
            max_flow=5,
            ):
        '''create a grid of cells

            the cell holds water (self.quantity)

            water has some momentum
            when it enters from a side it wants to exit from the other
            if the cell is not full not all will exit?

            gravity affects how much it goes out of a side

            if it is overfull it flows kinda everywhere
            also above
            '''

        self.rows = rows
        self.columns = columns

        self.gravity = gravity
        self.max_capacity = max_capacity
        self.max_flow = max_flow
        self.max_flow_gravity = max_flow

        self.quantity = np.zeros( (self.rows, self.columns) )

        self.flow_in_right = np.zeros( (self.rows, self.columns) )
        self.flow_in_left = np.zeros( (self.rows, self.columns) )
        self.flow_in_top = np.zeros( (self.rows, self.columns) )
        self.flow_in_bottom = np.zeros( (self.rows, self.columns) )

        self.flow_out_right = np.zeros( (self.rows, self.columns) )
        self.flow_out_left = np.zeros( (self.rows, self.columns) )
        self.flow_out_top = np.zeros( (self.rows, self.columns) )
        self.flow_out_bottom = np.zeros( (self.rows, self.columns) )

    def flow_step(self):
        '''compute one step'''

    def fill_bottom(self, depth, qty, waviness=0):
        '''initialize the bucket up to the specified depth and waviness'''
        #  self.quantity[:,1:2] = qty
        # if depth is more than self.columns this automagically works
        self.quantity[-depth:,:] = qty

    def add_drop(self, row, column, radius, qty):
        '''place a drop in the specified position'''
        radiussquared = radius**2
        for r in range(-radius, radius+1):
            for c in range(-radius, radius+1):
                if r**2 + c**2 <= radiussquared:
                    #  if r+row>=0 and c+column>=0:
                    if 0<= r+row < self.rows and 0<= c+column < self.columns:
                        #  print(f'r {r} c {c} r+row {r+row} c+column {c+column}')
                        self.quantity[r+row][c+column] += qty

    def evolve():
        '''apply movements on the map

        the idea is
        gather the input from all directions
        the water has momentum
        add some gravity
        if we put the output in flow_out_top my dudes everything gets mixed
        '''

    def print_qty(self):
        '''print the values'''
        #  '''print the values, saturated in proportion to capacity'''
        print(f'bucket shape {self.quantity.shape}')
        print(f'bucket\n{self.quantity}')
        for row in self.quantity:
            for q in row:
                #  print(f'{q: 3.0f}', end='') # no fractional part
                print(f'{q: 5.2f}', end='')
            print()

    def get_str_qty_small(self, char_wid=2):
        '''return a str of the values'''
        #  '''print the values, saturated in proportion to capacity'''
        #  print(f'bucket shape {self.quantity.shape}')
        #  print(f'bucket\n{self.quantity}')
        #  char_wid = 2
        str_qty_small = ''
        for row in self.quantity:
            for q in row:
                #  print(f'{q: 3.0f}', end='') # no fractional part
                #  print(f'{q:1.0f}'[-1:], end='')
                #  print(f'{q:{char_wid}.0f}'[-char_wid:], end='')
                str_qty_small += f'{q:{char_wid}.0f}'[-char_wid:]
            #  print()
            str_qty_small += '\n'
        return str_qty_small

    def get_str_qty_small_saturated(self, char_wid=2):
        '''return a str of the values, saturated in proportion to capacity'''
        #  print(f'bucket shape {self.quantity.shape}')
        #  print(f'bucket\n{self.quantity}')
        #  char_wid = 2
        cs = '\x1b[38;2;{};{};{}m{}\x1b[0m'

        str_qty_col = ''
        for row in self.quantity:
            for q in row:
                r,g,b = self.evaluate_rgb_depth(q, 0, self.max_capacity)

                # format the number
                # remove floating part
                # chop it off at char_wid, keep from right
                str_q = f'{q:.0f}'[-char_wid:]
                pad_q = f'{str_q:_>{char_wid}}'
                col_q = cs.format(r,g,b,pad_q)

                str_qty_col += col_q

            str_qty_col += '\n'

        return str_qty_col

    def evaluate_rgb_depth(self, z, d_min, d_max):
        '''return the rgb value for saturation proportional to z in [d_min, d_max]'''

        hue = 4/6 # blue

        frac = 0.4
        if d_max <= d_min:
        #  if d_max == d_min:
            saturation = frac
        else:
            # linear mapping z to saturation
            saturation = (z-d_min) / (d_max-d_min)
            #  # reshape it with sqrt
            #  #  saturation = sqrt(saturation)
            #  sq_fr = frac
            #  saturation = sqrt( (saturation+sq_fr) / (1+sq_fr) )

        value = 1

        r, g, b = hsv_to_rgb(hue, saturation, value)
        r = floor(r * 255)
        g = floor(g * 255)
        b = floor(b * 255)

        #  print(f'saturation {saturation:.3f} z {z} r {r} g {g} b {b}')
        #  print(f'val {z:2d} d_min {d_min:4d} d_max {d_max:4d} sat {saturation}')
        #  form_char = '\x1b[38;2;{};{};{}m{:_>2}\033[0m'
        #  f_c = f'{str(z)[-2:]}'
        #  print(f'val {z} r {r:4d} g {g:4d} b {b:4d} : {form_char.format(r, g, b, f_c)}')
        return r, g, b

    def print_image(self):
        '''use opencv to print the state of the holder'''
