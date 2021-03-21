class Cell:
    def __init__(self,
            capacity,
            max_capacity=100,
            max_flow=10,
            ):
        '''create a cell

        the cell holds water

        water has some momentum
        when it enters from a side it wants to exit from the other
        if the cell is not full not all will exit?

        gravity affects how much it goes out of a side

        if it is overfull it flows kinda everywhere
        '''

        self.capacity = capacity
        self.max_capacity = max_capacity

        # this is a lot cleaner but sadly far slower
        # TOP RIGHT BOTTOM LEFT NESW
        self.flow_in = [0, 0, 0, 0]
        self.flow_out = [0, 0, 0, 0]



