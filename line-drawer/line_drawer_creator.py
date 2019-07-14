import cv2
import logging
import numpy as np

from math import cos, sin
from math import floor
from math import pi
from timeit import default_timer as timer

from bresenham_generator import bresenham_generator


class Liner:
    """draw an image using a string from point to point on a circle

    draw lines from point to point
    """

    class_logger_loaded = False

    def __init__(
        self,
        path_input,
        path_output="out_img.png",
        num_corners=100,
        output_size=200,
        max_line_len=100,
        line_weight=100,
        top_left_x=230,
        top_left_y=210,
    ):

        self.setup_class_logger()
        initlog = logging.getLogger(f"{self.__class__.__name__}.console.init")
        #  initlog.setLevel("INFO")
        initlog.setLevel("DEBUG")

        self.path_input = path_input
        self.path_output = path_output

        self.num_corners = num_corners
        self.output_size = output_size
        self.radius = self.output_size // 2 - 1
        initlog.debug(f"output_size {self.output_size} radius {self.radius}")

        self.max_line_len = max_line_len
        self.line_weight = line_weight

        self.top_left_x = top_left_x
        self.top_left_y = top_left_y

        self.line = []

        ######################################################################
        # LOAD image
        self.img = cv2.imread(self.path_input, cv2.IMREAD_GRAYSCALE)

        if self.img is None:
            initlog.critical(f"Empty {self.path_input}")

        initlog.debug(f"Shape of img {self.img.shape} dtype {self.img.dtype}")
        initlog.debug(
            f"In img[100][100] {self.img[100][100]} type {type(self.img[100][100])}"
        )

        ######################################################################
        # create the MASK
        # some say dtype should be img.dtype stackoverflow.com/a/25075301
        self.circle_mask = np.zeros(
            (self.output_size, self.output_size), dtype=self.img.dtype
        )

        initlog.debug(f"Shape circle_mask {self.circle_mask.shape}")

        cv2.circle(
            self.circle_mask,
            center=(self.output_size // 2, self.output_size // 2),
            radius=self.radius,
            color=255,
            thickness=-1,
        )

        # show the mask
        #  cv2.imshow('mask circle', self.circle_mask)
        #  cv2.waitKey(0)

        ######################################################################
        # CROP the image and mask it
        # top left corner of the circle in the image
        x = self.top_left_x
        y = self.top_left_y

        # allocate the entire image
        self.img_crop = np.zeros(
            (self.output_size, self.output_size), dtype=self.img.dtype
        )

        # copy the relevant part, if it is smaller you'll get a black border
        temp = self.img[x + 0 : x + self.output_size, y + 0 : y + self.output_size]
        initlog.debug(f"Shape temp {temp.shape}")

        #  self.img_crop[x+0:x+self.output_size, y+0:y+self.output_size] =
        self.img_crop[0 : temp.shape[0], 0 : temp.shape[1]] = temp
        initlog.debug(f"Shape crop {self.img_crop.shape}")

        # show the cropped image
        #  cv2.imshow('cropped image', self.img_crop)
        #  cv2.waitKey(0)

        self.img_masked = cv2.bitwise_and(
            self.img_crop, self.img_crop, mask=self.circle_mask
        )

        # rescale the image
        self.img_masked = self.img_masked.astype(np.uint16)
        self.img_masked = self.img_masked * 256

        #  cv2.imshow("masked image", self.img_masked)
        #  cv2.waitKey(0)

        ######################################################################
        # generate the PINS for the line
        self.pins = np.zeros((self.num_corners, 2), dtype=np.uint16)
        theta = 2 * pi / self.num_corners
        for i in range(self.num_corners):
            #  self.pins[i, 0] = cos(theta * i) * self.radius + self.radius
            #  self.pins[i, 1] = sin(theta * i) * self.radius + self.radius
            self.pins[i, 0] = floor(cos(theta * i) * self.radius) + self.radius + 1
            self.pins[i, 1] = floor(sin(theta * i) * self.radius) + self.radius + 1

        initlog.debug(f"Pin 1 {self.pins[1]}")

    def setup_class_logger(self):
        """Setup a class wide logger
        """
        # this is run only the first time
        if Liner.class_logger_loaded is False:
            self.clalog = logging.getLogger(f"{self.__class__.__name__}.console")
            self.clalog.propagate = False

            self.clalog.setLevel("DEBUG")

            module_console_handler = logging.StreamHandler()

            #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            log_format_module = "%(name)s - %(levelname)s: %(message)s"
            #  log_format_module = '%(levelname)s: %(message)s'
            formatter = logging.Formatter(log_format_module)
            module_console_handler.setFormatter(formatter)

            self.clalog.addHandler(module_console_handler)

            logging.addLevelName(5, "TRACE")

            #  self.clalog.setLevel('TRACE')
            #  self.clalog.log(5, 'does this work')

            Liner.class_logger_loaded = True
