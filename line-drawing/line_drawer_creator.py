import cv2
import logging
import numpy as np

from math import pi
from math import cos
from math import sin
from random import randint
from random import sample
from timeit import default_timer as timer

class liner:
    '''draw an image using a string from point to point on a circle

    draw lines from point to point
    compute difference from original, use as loss
    either
        * add another point at the end
        * move a point -> VERY intensive
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
        initlog.setLevel('INFO')

        self.path_input = path_input
        self.path_output = path_output

        self.num_corners = num_corners
        self.output_size = output_size
        self.radius = self.output_size//2
        self.line_weight=line_weight

        self.line = []

        ######################################################################
        # LOAD image
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

        #  cv2.imshow('cropped image', self.img_crop)
        #  cv2.waitKey(0)

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

        initlog.debug(f'Pin 1 {self.pins[1]}')

    def compute_line(self):
        '''go through the line you have drawn so far and create the image
        '''

        drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint16)
        #  drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint8)

        #  cv2.imshow('generated image', drawn)
        #  cv2.waitKey(0)

    def stats(self):
        '''print info
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.stats')

        #  testlog.info(f'Sum of img_masked {np.sum(self.img_masked)}')
        testlog.info(f'Sum of img_crop {np.sum(self.img_crop)}')
        testlog.info(f'Shape of img_crop {self.img_crop.shape}')
        pixels = self.img_crop.shape[0] * self.img_crop.shape[1]
        testlog.info(f'Average of img_crop {np.sum(self.img_crop)/pixels}')

    def benchmark_looping_line(self):
        '''How slow is looping over an entire matrix?
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.benchll')
        testlog.setLevel('INFO')
        x = 1000
        y = 1000
        test_line_weight = 1

        line = np.zeros( (x,y), dtype=np.uint16)
        cv2.line(line, (1, 1), (1,8), test_line_weight)
        start = timer()
        for row in line:
            for bit in row:
                if bit == test_line_weight:
                    testlog.debug(f'Trovato {bit}')
        end = timer()
        testlog.info(f'Time to loop over {x*y} cells: {end-start}')
        # 1 second for 1M cells... 

        #  line = np.zeros( (x,y), dtype=np.uint16)
        #  cv2.line(line, (1, 1), (1,8), test_line_weight)
        #  start = timer()
        #  for i in range(x):
            #  for j in range(y):
                #  if line[i,j] == test_line_weight:
                    #  testlog.debug(f'Trovato {bit}')
        #  end = timer()
        #  testlog.info(f'Time to explicitly loop over {x*y} cells: {end-start}')

        drawn = np.zeros( (x,y), dtype=np.uint16)
        line = np.zeros( (x,y), dtype=np.uint16)

        start = timer()
        cv2.line(line, (1, 1), (x-1,y-1), test_line_weight)
        drawn = cv2.add(drawn , line)
        end = timer()
        testlog.info(f'Time to sum {x*y} cells: {end-start}')
        # 0.002 s for a 1000x1000

        start = timer()
        line = line.astype(np.int16)
        end = timer()
        testlog.info(f'Time to cast {x*y} cells: {end-start}')
        # 0.001 s for a 1000x1000

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
                #  (8, 1), (1,4),
                1000
                )

        testlog.debug(f'LINE\n{line}')

        drawn = cv2.add(drawn , line)
        testlog.debug(f'DRAWN\n{drawn}')

        #  cv2.imshow('generated image', drawn)
        #  cv2.waitKey(0)

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

        empty_line = np.zeros( (self.output_size+1, self.output_size+1), dtype=np.uint16)
        line = np.zeros( (self.output_size+1, self.output_size+1), dtype=np.uint16)
        for i in range(len(test_line)-1):
            start = test_line[i]
            end = test_line[i+1]
            #  testlog.debug(f'{start} {end}')

            #  pin_start = self.pins[start]
            #  pin_end = self.pins[end]
            psx, psy = self.pins[start]
            pex, pey = self.pins[end]

            # this feels BAD, allocating one each time
            #  line = np.zeros( (self.output_size+1, self.output_size+1), dtype=np.uint16)
            # tho I'm not sure what copyTo does inside
            line = cv2.copyTo(empty_line, None)
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

    def test_loss(self):
        '''Experiments on how to compute decently the error from the line

        If I just look at the difference (target-drawn) the best line will be
        the longest one (all the pixels in every line will improve the result)
        until the pixels along that diameter go over the target and lines
        progressively shorter will be considered, but I bet there will be a
        bright spot in the middle.

        Looking at the difference (target-drawn) *only* along the line might be
        more promising, as the bright corridor only needs to be filled until
        another has similar error. This is very intensive I guess, as you have
        to iterate over all the pixels to find if they are a linepixel or not.

        To avoid looping over the entire matrix to find the line, a separate
        algorithm might be useful
        https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm

        Weighting the improvement with the line length might improve the
        results, as longer lines have more "residual difference" than shorter
        ones. To avoid weird effects when weighting, some parameters might be tuned:

            res_diff = (target-drawn)|along the line
            wei_res_diff = res_diff / (line_length+1)

        You pick the one with the *highest* residual difference, so when along
        a line the drawn is already brighter than the target, that is less
        likely to be picked

        Yeah all that might define a discrete prob distribution, and you pick
        the next pin accordingly
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.testlo')
        #  testlog.setLevel('TRACE')

        testlog.log(5, f'IMG MASKED\n{self.img_masked}')
        testlog.debug(f'IMG MASKED sum {np.sum(self.img_masked)}')

        test_line_weight = 1

        drawn = np.zeros( (11,11), dtype=np.uint16)

        residual = np.zeros( (11,11), dtype=np.int16)
        residual = cv2.copyTo(self.img_masked, None)
        testlog.log(5, f'RESIDUAL dtype after copy {type(residual[0,0])}')
        residual = residual.astype(np.int16)
        testlog.log(5, f'RESIDUAL dtype after magic {type(residual[0,0])}')

        #  self.test_draw_line(drawn, residual, (1, 1), (1,8), test_line_weight, 'DEBUG')
        self.test_draw_line(drawn, residual, (1, 1), (1,8), test_line_weight,)
        testlog.log(5, f'\n')
        testlog.log(5, f'DRAWN\n{drawn}')
        testlog.log(5, f'RESIDUAL\n{residual}')
        testlog.debug(f'RESIDUAL sum {np.sum(residual)}')

        self.test_draw_line(drawn, residual, (1, 8), (8,1), test_line_weight)
        testlog.log(5, f'\n')
        testlog.log(5, f'DRAWN\n{drawn}')
        testlog.log(5, f'RESIDUAL\n{residual}')
        testlog.debug(f'RESIDUAL sum {np.sum(residual)}')

        self.test_draw_line(drawn, residual, (8,1), (1,1), test_line_weight)
        testlog.log(5, f'\n')
        testlog.log(5, f'DRAWN\n{drawn}')
        testlog.log(5, f'RESIDUAL\n{residual}')
        testlog.debug(f'RESIDUAL sum {np.sum(residual)}')

        residual_abs = np.abs(residual)
        testlog.log(5, f'\n')
        testlog.log(5, f'RESIDUAL ABS\n{residual_abs}')
        testlog.debug(f'RESIDUAL ABS sum {np.sum(residual_abs)}')

        self.test_draw_line(drawn, residual, (1, 1), (1,8), test_line_weight,)
        testlog.log(5, f'\n')
        testlog.log(5, f'DRAWN\n{drawn}')
        testlog.log(5, f'RESIDUAL\n{residual}')
        testlog.debug(f'RESIDUAL sum {np.sum(residual)}')

        residual_abs = np.abs(residual)
        testlog.log(5, f'\n')
        testlog.log(5, f'RESIDUAL ABS\n{residual_abs}')
        testlog.debug(f'RESIDUAL ABS sum {np.sum(residual_abs)}')

    def test_draw_line(self, drawn, residual, x, y, test_line_weight, logLevel='INFO'):
        '''draw a line on drawn, subtract it from residual
        '''
        testlog = logging.getLogger(f'{self.__class__.__name__}.console.testdl')
        testlog.setLevel(logLevel)
        testlog.debug(f'Line from {x} to {y}')
        line = np.zeros( (11,11), dtype=np.uint16)
        cv2.line(line, x, y, test_line_weight)
        # remove the last dot from the line
        # WHAT
        line[y[1], y[0]] -= test_line_weight
        testlog.debug(f'the LINE\n{line}')
        cv2.add(drawn , line, drawn)
        line_int = line.astype(np.int16)
        cv2.subtract(residual, line_int, residual)

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

        logging.addLevelName(5, 'TRACE')

        #  self.clalog.setLevel('TRACE')
        #  self.clalog.log(5, 'does this work')
