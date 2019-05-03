import numpy as np

class Holder:
    def __init__(self,
            rows,
            columns,
            gravity=10,
            max_capacity=100,
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

        self.quantity = np.zeros( (self.rows, self.columns) )
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
                print(f'r {r} c {c}')
                if r**2 + c**2 <= radiussquared:
                    if r+row>=0 and c+column>=0:
                        self.quantity[r+row][c+column] += qty

    def print_qty(self):
        '''print the values, saturated in proportion to capacity'''
        print(f'bucket shape {self.quantity.shape}')
        print(f'bucket\n{self.quantity}')
        for row in self.quantity:
            for q in row:
                #  print(f'{q: 3.0f}', end='') # no fractional part
                print(f'{q: 5.2f}', end='')
            print()

    def print_qty_small(self):
        '''print the values, saturated in proportion to capacity'''
        #  print(f'bucket shape {self.quantity.shape}')
        #  print(f'bucket\n{self.quantity}')
        char_wid = 2
        for row in self.quantity:
            for q in row:
                #  print(f'{q: 3.0f}', end='') # no fractional part
                #  print(f'{q:1.0f}'[-1:], end='')
                print(f'{q:{char_wid}.0f}'[-char_wid:], end='')
            print()

    def print_image(self):
        '''use opencv to print the state of the holder'''
