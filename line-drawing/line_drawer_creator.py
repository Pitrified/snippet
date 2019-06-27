import cv2
import logging
import numpy as np

from math import pi
from math import cos
from math import sin
from random import randint
from random import sample

class liner:
    '''draw an image using a string from point to point on a circle

    draw lines from point to point
    compute difference from original, use as loss
    either
        * add another point at the end
        * move a point
    '''
    def __init__(self,
            path_input,
            path_output='out_img.jpg',
            num_corners=100,
            output_size=200,
            line_weight=1000,
            ):

        self.setup_class_logger()
        initlog = logging.getLogger(f'{self.__class__.__name__}.console.init')

        self.path_input = path_input
        self.path_output = path_output

        self.num_corners = num_corners
        self.output_size = output_size
        self.radius = self.output_size//2
        self.line_weight=line_weight

        self.line = []

        self.img = cv2.imread(self.path_input,
                cv2.IMREAD_GRAYSCALE)

        if self.img is None:
            initlog.critical(f'Empty {self.path_input}')

        initlog.debug(f'Shape of img {self.img.shape} dtype {self.img.dtype}')
        initlog.debug(f'In img[100][100] {self.img[100][100]} type {type(self.img[100][100])}')

        ######################################################################
        # create the MASK
        # some say dtype should be img.dtype stackoverflow.com/a/25075301
        self.circle_mask = np.zeros( (self.output_size, self.output_size),
                dtype=self.img.dtype )

        initlog.debug(f'Shape circle_mask {self.circle_mask.shape}')

        cv2.circle(self.circle_mask,
                center=(self.output_size//2, self.output_size//2),
                radius=self.output_size//2,
                color = 255,
                thickness = -1,
                )

        # show the mask
        #  cv2.imshow('mask circle', self.circle_mask)
        #  cv2.waitKey(0)

        ######################################################################
        # CROP the image and mask it
        # top left corner of the circle in the image
        x = 230
        y = 210
        #  x = 0
        #  y = 0

        # allocate the entire image
        self.img_crop = np.zeros( (self.output_size, self.output_size),
                dtype=self.img.dtype )

        # copy the relevant part, if it is smaller you'll get a black border
        temp = self.img[x+0:x+self.output_size, y+0:y+self.output_size]
        initlog.debug(f'Shape temp {temp.shape}')

        #  self.img_crop[x+0:x+self.output_size, y+0:y+self.output_size] = 
        self.img_crop[ 0:temp.shape[0], 0:temp.shape[1] ] = temp
        initlog.debug(f'Shape crop {self.img_crop.shape}')

        cv2.imshow('cropped image', self.img_crop)
        cv2.waitKey(0)

        self.img_masked = cv2.bitwise_and(self.img_crop, self.img_crop,
                mask=self.circle_mask)

        #  cv2.imshow('masked image', self.img_masked)
        #  cv2.waitKey(0)

        ######################################################################
        # generate the PINS for the line
        self.pins = np.zeros( (self.num_corners, 2), dtype=np.uint16 )
        theta = 2 * pi / self.num_corners
        for i in range(self.num_corners):
            self.pins[i, 0] = cos(theta * i) * self.radius + self.radius
            self.pins[i, 1] = sin(theta * i) * self.radius + self.radius

        initlog.debug(f'Pin 10 {self.pins[10]}')

    def compute_line(self):
        '''go through the line you have drawn so far and create the image
        '''

        drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint16)
        #  drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint8)

        #  cv2.circle(drawn,
                #  center=(self.output_size//2, self.output_size//2),
                #  radius=self.output_size//2,
                #  #  color = 255, # for uint8
                #  color = 65535, # match the dtype
                #  thickness = 1,
                #  )

        cv2.imshow('generated image', drawn)
        cv2.waitKey(0)

    def test_line_shading(self):
        '''Test how summing lines works
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.testls')

        drawn = np.zeros( (10,10), dtype=np.uint16)
        pins = np.array( [[1,1], [1,8], [8,1], [8,8] ] )

        white = 65535
        for x,y in pins:
            #  testlog.debug(f'Pin x y {x} {y}')
            drawn[x,y] = white

        # first line
        line = np.zeros( (10,10), dtype=np.uint16)
        cv2.line(line,
                (1, 1), (1,8),
                1000
                )
        testlog.debug(f'LINE\n{line}')

        # add it
        drawn = cv2.add(drawn , line)
        testlog.debug(f'DRAWN\n{drawn}')


        # second line
        line = np.zeros( (10,10), dtype=np.uint16)
        cv2.line(line,
                (8, 1), (1,8),
                1000
                )
        testlog.debug(f'LINE\n{line}')

        # add it
        drawn = cv2.add(drawn , line)
        testlog.debug(f'DRAWN\n{drawn}')

        cv2.line(line,
                (8, 1), (1,8),
                1000
                )

        testlog.debug(f'LINE\n{line}')

        drawn = cv2.add(drawn , line)
        testlog.debug(f'DRAWN\n{drawn}')

        cv2.imshow('generated image', drawn)
        cv2.waitKey(0)

    def test_pins_line(self, num_points = 2000):
        '''Draw the pins and some example lines
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.testpl')

        drawn = np.zeros( (self.output_size+1, self.output_size+1), dtype=np.uint16)
        #  drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint8)
        white = 65535
        for x,y in self.pins:
            #  testlog.debug(f'Pin x y {x} {y}')
            drawn[x,y] = white

        #  num_points = 2000
        test_line = self.generate_test_line(num_points, self.num_corners)

        for i in range(len(test_line)-1):
            start = test_line[i]
            end = test_line[i+1]
            #  testlog.debug(f'{start} {end}')

            #  pin_start = self.pins[start]
            #  pin_end = self.pins[end]
            psx, psy = self.pins[start]
            pex, pey = self.pins[end]

            # this feels BAD, allocating one each time
            line = np.zeros( (self.output_size+1, self.output_size+1), dtype=np.uint16)
            cv2.line(line,
                    #  pin_start, pin_end,
                    (psx, psy), (pex,pey),
                    #  65535
                    self.line_weight,
                    )

            drawn = cv2.add(drawn , line)

        #  testlog.debug(f'{drawn}')

        cv2.imshow('generated image', drawn)
        cv2.waitKey(0)

    def generate_test_line(self, length, test_num_corners):
        '''generate a line with specified length and corners
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.testgl')

        test_line = np.zeros( length, np.uint16 )

        test_line[0], test_line[1] = sample(range(test_num_corners), 2)
        for i in range(1, length):
            # randint goes from (a,b) included, if I ask 100 corners I want 0,99
            corner = randint(0, test_num_corners-1)
            # cant be like the last one, and the one before
            # 10 15 10 is not allowed, nor 10 10
            while corner == test_line[i-1] or corner == test_line[i-2]:
                corner = randint(0, test_num_corners-1)
            test_line[i] = corner

        #  testlog.debug(f'{test_line}')
        return test_line


    def setup_class_logger(self):
        self.clalog = logging.getLogger(f'{self.__class__.__name__}.console')
        self.clalog.propagate = False

        self.clalog.setLevel('DEBUG')

        module_console_handler = logging.StreamHandler()

        #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_format_module = '%(name)s - %(levelname)s: %(message)s'
        #  log_format_module = '%(levelname)s: %(message)s'
        formatter = logging.Formatter(log_format_module)
        module_console_handler.setFormatter(formatter)

        self.clalog.addHandler(module_console_handler)
