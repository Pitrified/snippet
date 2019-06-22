import cv2
import logging
import numpy as np

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
            ):

        self.setup_class_logger()

        self.path_input = path_input
        self.path_output = path_output

        self.num_corners = num_corners
        self.output_size = output_size

        self.line = []

        self.img = cv2.imread(self.path_input,
                cv2.IMREAD_GRAYSCALE)

        if self.img is None:
            #  print(f'Empty {self.path_input}')
            self.clalog.critical(f'Empty {self.path_input}')

        self.clalog.debug(f'Shape of img {self.img.shape} dtype {self.img.dtype}')
        self.clalog.debug(f'In img[100][100] {self.img[100][100]} type {type(self.img[100][100])}')

        # some say dtype should be img.dtype stackoverflow.com/a/25075301
        self.circle_mask = np.zeros( (self.output_size, self.output_size),
                dtype=self.img.dtype )

        cv2.circle(self.circle_mask,
                center=(self.output_size//2, self.output_size//2),
                radius=self.output_size//2,
                #  color = 1,
                color = 255,
                thickness = -1,
                )

        #  cv2.imshow('mask circle', self.circle_mask)
        #  cv2.waitKey(0)

        x = 200
        y = 200
        self.img_crop = self.img[x+0:x+self.output_size, y+0:y+self.output_size]

        self.img_masked = cv2.bitwise_and(self.img_crop, self.img_crop,
                mask=self.circle_mask)
        #  cv2.imshow('masked image', self.img_masked)
        #  cv2.waitKey(0)

    def compute_line(self):
        '''go through the line you have drawn so far and create the image
        '''

        drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint16)
        #  drawn = np.zeros( (self.output_size, self.output_size), dtype=np.uint8)

        cv2.circle(drawn,
                center=(self.output_size//2, self.output_size//2),
                radius=self.output_size//2,
                #  color = 255, # for uint8
                color = 65535, # match the dtype
                thickness = 1,
                )

        cv2.imshow('generated image', drawn)
        cv2.waitKey(0)

    def setup_class_logger(self):
        self.clalog = logging.getLogger(f'{self.__class__.__name__}.console')
        self.clalog.propagate = False

        self.clalog.setLevel('DEBUG')

        module_console_handler = logging.StreamHandler()

        #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        log_format_module = '%(name)s - %(levelname)s: %(message)s'
        formatter = logging.Formatter(log_format_module)
        module_console_handler.setFormatter(formatter)

        self.clalog.addHandler(module_console_handler)
