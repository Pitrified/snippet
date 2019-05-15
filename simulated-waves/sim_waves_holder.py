import numpy as np
from colorsys import hsv_to_rgb
from math import floor
from math import sqrt

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

        #  self.flow_in_right = np.zeros( (self.rows, self.columns) )
        #  self.flow_in_left = np.zeros( (self.rows, self.columns) )
        #  self.flow_in_top = np.zeros( (self.rows, self.columns) )
        #  self.flow_in_bottom = np.zeros( (self.rows, self.columns) )

        # TOP RIGHT BOTTOM LEFT

        self.flow_in= [
                np.zeros( (self.rows, self.columns) ),
                np.zeros( (self.rows, self.columns) ),
                np.zeros( (self.rows, self.columns) ),
                np.zeros( (self.rows, self.columns) ),
                ]

        #  self.flow_out_right = np.zeros( (self.rows, self.columns) )
        #  self.flow_out_left = np.zeros( (self.rows, self.columns) )
        #  self.flow_out_top = np.zeros( (self.rows, self.columns) )
        #  self.flow_out_bottom = np.zeros( (self.rows, self.columns) )

        self.reset_flow_out()

    def reset_flow_out(self):
        self.flow_out = [
                np.zeros( (self.rows, self.columns) ),
                np.zeros( (self.rows, self.columns) ),
                np.zeros( (self.rows, self.columns) ),
                np.zeros( (self.rows, self.columns) ),
                ]

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

    def evolve(self):
        '''apply movements on the map

        the idea is
        gather the input from all directions flow_in_top

        the water has momentum
        which is slightly dampened each time
        the dampening might be proportional to the quantity of water

        add some gravity

        if the cell below is full
        and some water needs to go down then splash it around
        because the water HAS momentum, so the cell below can be invaded

        we put the output in flow_out_top
        '''

        dampening = 0.1

        # build flow_in from previous flow_out
        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):

                ### flow along columns
                # first row
                if i == 0:
                    # edges are bounced back
                    self.flow_in[0][i][j] = self.flow_out[0][i][j]
                    self.flow_in[2][i][j] = self.flow_out[0][i+1][j]

                # bottom row
                elif i == self.rows - 1:
                    self.flow_in[0][i][j] = self.flow_out[2][i-1][j]
                    self.flow_in[2][i][j] = self.flow_out[2][i][j]

                # middle rows: now we have to check if you are in a correct column
                # NOT! we only do top 0 bottom 2 now
                #  elif 0 < j < self.columns - 1:
                else:
                    self.flow_in[0][i][j] = self.flow_out[2][i-1][j]
                    self.flow_in[2][i][j] = self.flow_out[0][i+1][j]

                ### flow along rows
                # left column
                if j == 0:
                    self.flow_in[1][i][j] = self.flow_out[1][i][j]
                    self.flow_in[3][i][j] = self.flow_out[1][i][j+1]

                # right column
                elif j == self.columns - 1:
                    self.flow_in[1][i][j] = self.flow_out[3][i][j-1]
                    self.flow_in[3][i][j] = self.flow_out[3][i][j]

                else:
                    self.flow_in[1][i][j] = self.flow_out[3][i][j-1]
                    self.flow_in[3][i][j] = self.flow_out[1][i][j+1]

        self.reset_flow_out()

        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):

                # water entering basically flows through
                for direction in range(4):
                    f_in = self.flow_in[direction][i][j]
                    self.flow_out[(direction+4)%4][i][j] += f_in * dampening
                    self.quantity[i][j] += f_in * (1-dampening)

                # gravity
                if self.quantity[i][j] > self.max_flow_gravity:
                    grav_qty = self.max_flow_gravity
                    self.quantity[i][j] -= self.max_flow_gravity
                else:
                    grav_qty = self.quantity[i][j]
                    self.quantity[i][j] = 0
                self.flow_out[2][i][j] += grav_qty

                # is overflowing?
                if self.quantity[i][j] > self.max_capacity:
                    over_qty = self.max_capacity - self.quantity[i][j] 
                    for direction in range(4):
                        # splash EVERYWEHRHRE
                        self.flow_out[direction][i][j] += over_qty / 4

                # NOTE might do this in the flow_out > flow_in
                #  # edges are bounced back
                #  # first row
                #  if i == 0:
                    #  self.flow_in[0][i][j] = self.flow_out[0][i][j]

                #  # bottom row
                #  if i == self.rows:
                    #  self.flow_in[2][i][j] = self.flow_out[2][i][j]

                #  # left column
                #  if j == 0:
                    #  self.flow_in[1][i][j] = self.flow_out[1][i][j]

                #  # right column
                #  if j == self.columns:
                    #  self.flow_in[3][i][j] = self.flow_out[3][i][j]

    def evolve_steps(self):
        '''do evolution in steps so we can debug even more'''

        str_evolve_debug = ''

        str_evolve_debug += f'\n###############\nStarting evolution:\n'
        str_evolve_debug += f'{self.get_str_recap_sat(3)}\n'

        # build QTY: remove from OUT
        self.qty_remove_out()
        str_evolve_debug += f'Removed out\n'
        str_evolve_debug += f'{self.get_str_recap_sat(3)}\n'

        # build IN from previous OUT status
        self.evolve_out_to_in()
        str_evolve_debug += f'Evolved out to in\n'
        str_evolve_debug += f'{self.get_str_recap_sat(3)}\n'

        self.reset_flow_out()

        # build OUT
        # using info also from IN (e.g. momentum)
        # do NOT modify QTY
        self.evolve_momentum()
        self.evolve_gravity()
        self.evolve_diffusion()
        str_evolve_debug += f'Applied evolve\n'
        str_evolve_debug += f'{self.get_str_recap_sat(3)}\n'

        # build QTY: add from IN
        self.qty_add_in()
        str_evolve_debug += f'Added in\n'
        str_evolve_debug += f'{self.get_str_recap_sat(3)}\n'

        # print HERE
        #  print(f'Done evolving')
        #  print(f'{self.get_str_recap_sat(3)}')

        return str_evolve_debug

    def evolve_out_to_in(self):
        '''shuffle info around, from out (of previous step) to in'''
        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):

                ### flow along columns
                # first row
                if i == 0:
                    # edges are bounced back
                    self.flow_in[0][i][j] = self.flow_out[0][i][j]
                    self.flow_in[2][i][j] = self.flow_out[0][i+1][j]

                # bottom row
                elif i == self.rows - 1:
                    self.flow_in[0][i][j] = self.flow_out[2][i-1][j]
                    self.flow_in[2][i][j] = self.flow_out[2][i][j]

                # middle rows: now we have to check if you are in a correct column
                # NOT! we only do top 0 bottom 2 now
                #  elif 0 < j < self.columns - 1:
                else:
                    self.flow_in[0][i][j] = self.flow_out[2][i-1][j]
                    self.flow_in[2][i][j] = self.flow_out[0][i+1][j]

                ### flow along rows
                # left column
                if j == 0:
                    self.flow_in[1][i][j] = self.flow_out[1][i][j]
                    self.flow_in[3][i][j] = self.flow_out[1][i][j+1]

                # right column
                elif j == self.columns - 1:
                    self.flow_in[1][i][j] = self.flow_out[3][i][j-1]
                    self.flow_in[3][i][j] = self.flow_out[3][i][j]

                else:
                    self.flow_in[1][i][j] = self.flow_out[3][i][j-1]
                    self.flow_in[3][i][j] = self.flow_out[1][i][j+1]

    def evolve_momentum(self):
        '''water entering basically flows through'''

        dampening = 0.1

        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):
                for direction in range(4):
                    f_in = self.flow_in[direction][i][j]
                    self.flow_out[(direction+4)%4][i][j] += f_in * dampening
                    #  self.quantity[i][j] += f_in * (1-dampening)

    def evolve_gravity(self):
        '''do gravity evolution, put some water from quantity to flow_out

        this might be not limited by max_flow_gravity directly, but
        proportionately with the quantity or even the whole quantity, it's not
        like a drop of water flows in stages
        '''
        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):

                if self.quantity[i][j] > self.max_flow_gravity:
                    grav_qty = self.max_flow_gravity
                    #  self.quantity[i][j] -= self.max_flow_gravity
                else:
                    grav_qty = self.quantity[i][j]
                    #  self.quantity[i][j] = 0

                self.flow_out[2][i][j] += grav_qty

    def evolve_diffusion(self):
        '''some water just goes to nearby cells'''

        diff_frac = 0.1

        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):
                diff_qty = q * diff_frac

                for direction in range(4):
                    self.flow_out[direction][i][j] += diff_qty

    def qty_add_in(self):
        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):
                tot_flow_in = 0
                for direction in range(4):
                    tot_flow_in += self.flow_in[direction][i][j]
                self.quantity[i][j] += tot_flow_in

    def qty_remove_out(self):
        for i, row in enumerate(self.quantity):
            for j, q in enumerate(row):
                tot_flow_out = 0
                for direction in range(4):
                    tot_flow_out += self.flow_out[direction][i][j]
                self.quantity[i][j] -= tot_flow_out

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

    def get_str_flow_in(self, char_wid=2):
        lfi_top = self.get_str_flow_in_dir(0, char_wid).split('\n')
        lfi_right = self.get_str_flow_in_dir(1, char_wid).split('\n')
        lfi_bottom = self.get_str_flow_in_dir(2, char_wid).split('\n')
        lfi_left = self.get_str_flow_in_dir(3, char_wid).split('\n')

        str_flow_in = ''
        for t, r, b, l in zip( lfi_top, lfi_right, lfi_bottom, lfi_left):
            str_flow_in += f'{t}  {r}  {b}  {l}\n'
        #  return str_flow_in
        return str_flow_in[:-1] # chop off double \n

    def get_str_flow_in_dir(self, direction, char_wid=2):
        str_flow_in_dir = ''
        for row in self.flow_in[direction]:
            for q in row:
                str_flow_in_dir += f'{q:{char_wid}.0f}'[-char_wid:]
            str_flow_in_dir += '\n'
        return str_flow_in_dir

    def get_str_flow_out(self, char_wid=2):
        lfi_top = self.get_str_flow_out_dir(0, char_wid).split('\n')
        lfi_right = self.get_str_flow_out_dir(1, char_wid).split('\n')
        lfi_bottom = self.get_str_flow_out_dir(2, char_wid).split('\n')
        lfi_left = self.get_str_flow_out_dir(3, char_wid).split('\n')

        str_flow_out = ''
        for t, r, b, l in zip( lfi_top, lfi_right, lfi_bottom, lfi_left):
            str_flow_out += f'{t}  {r}  {b}  {l}\n'
        #  return str_flow_out
        return str_flow_out[:-1] # chop off double \n

    def get_str_flow_out_dir(self, direction, char_wid=2):
        str_flow_out_dir = ''
        for row in self.flow_out[direction]:
            for q in row:
                str_flow_out_dir += f'{q:{char_wid}.0f}'[-char_wid:]
            str_flow_out_dir += '\n'
        return str_flow_out_dir

    def get_str_recap(self, char_wid=2):
        lfi_top = self.get_str_flow_in_dir(0, char_wid).splitlines()
        lfi_right = self.get_str_flow_in_dir(1, char_wid).splitlines()
        lfi_bottom = self.get_str_flow_in_dir(2, char_wid).splitlines()
        lfi_left = self.get_str_flow_in_dir(3, char_wid).splitlines()

        lfo_top = self.get_str_flow_out_dir(0, char_wid).splitlines()
        lfo_right = self.get_str_flow_out_dir(1, char_wid).splitlines()
        lfo_bottom = self.get_str_flow_out_dir(2, char_wid).splitlines()
        lfo_left = self.get_str_flow_out_dir(3, char_wid).splitlines()

        lqty = self.get_str_qty_small(char_wid).splitlines()

        tab_wid = self.columns * char_wid + 2
        header = f'{{:^{tab_wid}}}'
        #  print(header)

        str_recap = ''

        str_recap += header.format('IN top')
        str_recap += header.format('OUT top')
        str_recap += header.format('IN right')
        str_recap += '\n'

        for a, b, c in zip( lfi_top, lfo_top, lfi_right):
            str_recap += f'{a}  {b}  {c}\n'

        str_recap += header.format('OUT left')
        str_recap += header.format('QTY')
        str_recap += header.format('OUT right')
        str_recap += '\n'

        for a, b, c in zip( lfo_left, lqty, lfo_right):
            str_recap += f'{a}  {b}  {c}\n'

        str_recap += header.format('IN left')
        str_recap += header.format('OUT bottom')
        str_recap += header.format('IN bottom')
        str_recap += '\n'

        for a, b, c in zip( lfi_left, lfo_bottom, lfi_bottom):
            str_recap += f'{a}  {b}  {c}\n'

        return str_recap

    def get_str_sum_info(self):
        str_info = ''

        sum_qty = np.sum(self.quantity)
        str_info += f'Sum qty: {sum_qty}'
        return str_info

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

    def get_str_flow_in_sat(self, char_wid=2):
        lfi_top = self.get_str_flow_in_dir_sat(0, char_wid).split('\n')
        lfi_right = self.get_str_flow_in_dir_sat(1, char_wid).split('\n')
        lfi_bottom = self.get_str_flow_in_dir_sat(2, char_wid).split('\n')
        lfi_left = self.get_str_flow_in_dir_sat(3, char_wid).split('\n')

        str_flow_in_sat = ''
        for t, r, b, l in zip( lfi_top, lfi_right, lfi_bottom, lfi_left):
            str_flow_in_sat += f'{t}  {r}  {b}  {l}\n'
        #  return str_flow_in_sat
        return str_flow_in_sat[:-1] # chop off double \n

    def get_str_flow_in_dir_sat(self, direction, char_wid=2):
        cs = '\x1b[38;2;{};{};{}m{}\x1b[0m'

        max_q = np.amax(self.flow_out[direction])

        str_flow_in_dir_sat = ''
        for row in self.flow_in[direction]:
            for q in row:
                #  r,g,b = self.evaluate_rgb_depth(q, 0, self.max_capacity, 0)
                r,g,b = self.evaluate_rgb_depth(q, 0, max_q, 1/6)

                str_q = f'{q:.0f}'[-char_wid:]
                pad_q = f'{str_q:_>{char_wid}}'
                col_q = cs.format(r,g,b,pad_q)
                str_flow_in_dir_sat += col_q

            str_flow_in_dir_sat += '\n'
        return str_flow_in_dir_sat

    def get_str_flow_out_sat(self, char_wid=2):
        lfi_top = self.get_str_flow_out_dir_sat(0, char_wid).split('\n')
        lfi_right = self.get_str_flow_out_dir_sat(1, char_wid).split('\n')
        lfi_bottom = self.get_str_flow_out_dir_sat(2, char_wid).split('\n')
        lfi_left = self.get_str_flow_out_dir_sat(3, char_wid).split('\n')

        str_flow_out_sat = ''
        for t, r, b, l in zip( lfi_top, lfi_right, lfi_bottom, lfi_left):
            str_flow_out_sat += f'{t}  {r}  {b}  {l}\n'
        #  return str_flow_out_sat
        return str_flow_out_sat[:-1] # chop off double \n

    def get_str_flow_out_dir_sat(self, direction, char_wid=2):
        cs = '\x1b[38;2;{};{};{}m{}\x1b[0m'

        max_q = np.amax(self.flow_out[direction])

        str_flow_out_dir_sat = ''
        for row in self.flow_out[direction]:
            for q in row:
                #  r,g,b = self.evaluate_rgb_depth(q, 0, self.max_capacity, 0)
                r,g,b = self.evaluate_rgb_depth(q, 0, max_q, 0)

                str_q = f'{q:.0f}'[-char_wid:]
                pad_q = f'{str_q:_>{char_wid}}'
                col_q = cs.format(r,g,b,pad_q)
                str_flow_out_dir_sat += col_q

            str_flow_out_dir_sat += '\n'
        return str_flow_out_dir_sat

    def get_str_recap_sat(self, char_wid=2):
        lfi_top = self.get_str_flow_in_dir_sat(0, char_wid).splitlines()
        lfi_right = self.get_str_flow_in_dir_sat(1, char_wid).splitlines()
        lfi_bottom = self.get_str_flow_in_dir_sat(2, char_wid).splitlines()
        lfi_left = self.get_str_flow_in_dir_sat(3, char_wid).splitlines()

        lfo_top = self.get_str_flow_out_dir_sat(0, char_wid).splitlines()
        lfo_right = self.get_str_flow_out_dir_sat(1, char_wid).splitlines()
        lfo_bottom = self.get_str_flow_out_dir_sat(2, char_wid).splitlines()
        lfo_left = self.get_str_flow_out_dir_sat(3, char_wid).splitlines()

        lqty = self.get_str_qty_small_saturated(char_wid).splitlines()

        tab_wid = self.columns * char_wid + 2
        header = f'{{:^{tab_wid}}}'
        #  print(header)

        str_recap = ''

        str_recap += header.format('IN top')
        str_recap += header.format('OUT top')
        str_recap += header.format('IN right')
        str_recap += '\n'

        for a, b, c in zip( lfi_top, lfo_top, lfi_right):
            str_recap += f'{a}  {b}  {c}\n'

        str_recap += header.format('OUT left')
        str_recap += header.format('QTY')
        str_recap += header.format('OUT right')
        str_recap += '\n'

        for a, b, c in zip( lfo_left, lqty, lfo_right):
            str_recap += f'{a}  {b}  {c}\n'

        str_recap += header.format('IN left')
        str_recap += header.format('OUT bottom')
        str_recap += header.format('IN bottom')
        str_recap += '\n'

        for a, b, c in zip( lfi_left, lfo_bottom, lfi_bottom):
            str_recap += f'{a}  {b}  {c}\n'

        return str_recap

    def evaluate_rgb_depth(self, z, d_min, d_max, hue=4/6):
        '''return the rgb value for saturation proportional to z in [d_min, d_max]'''

        #  hue = 4/6 # blue

        #  frac = 0.4
        frac = 0.1
        if d_max <= d_min:
        #  if d_max == d_min:
            saturation = frac
            #  saturation = 0
        elif z < d_min:
            saturation = 1
            hue = 3/6
        elif z >= d_max:
            saturation = 1
        else:
            # linear mapping z to saturation
            saturation = (z-d_min) / (d_max-d_min)
            #  # reshape it with sqrt
            #  #  saturation = sqrt(saturation)
            sq_fr = frac
            saturation = sqrt( (saturation+sq_fr) / (1+sq_fr) )

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
