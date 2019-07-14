import cv2
import logging
import numpy as np

from math import cos, sin
from math import floor
from math import pi
from random import randint
from random import choices
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
        initlog.setLevel("INFO")
        #  initlog.setLevel("DEBUG")

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

        # compute line masks on the fly, burn memory to go faster
        self.line_mask = {}
        self.line_mask_weighted = {}

        ######################################################################
        # LOAD image
        self.img = cv2.imread(self.path_input, cv2.IMREAD_GRAYSCALE)

        if self.img is None:
            initlog.critical(f"Empty {self.path_input}")

        initlog.debug(f"Shape of img {self.img.shape} dtype {self.img.dtype}")
        initlog.debug(f"In img[5][5] {self.img[5][5]} type {type(self.img[5][5])}")

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

        # allocate an image as big as the requested output
        self.img_crop = np.zeros(
            (self.output_size, self.output_size), dtype=self.img.dtype
        )

        # copy the relevant part, if it overflows you get a smaller image
        temp = self.img[x + 0 : x + self.output_size, y + 0 : y + self.output_size]
        initlog.debug(f"Shape temp {temp.shape}")

        # copy the image in the allocated space
        self.img_crop[0 : temp.shape[0], 0 : temp.shape[1]] = temp
        initlog.debug(f"Shape crop {self.img_crop.shape}")

        # show the cropped image
        #  cv2.imshow('cropped image', self.img_crop)
        #  cv2.waitKey(0)

        # mask the image
        self.img_masked = cv2.bitwise_and(
            self.img_crop, self.img_crop, mask=self.circle_mask
        )

        # show the masked image
        #  cv2.imshow("masked image", self.img_masked)
        #  cv2.waitKey(0)

        # retype the image to avoid overflow problems
        self.img_objective = self.img_masked.astype(np.int16)

        # image built so far
        self.img_built = np.zeros_like(self.img_objective)

        # image of residual deltas
        self.img_residual = np.copy(self.img_objective)

        ######################################################################
        # generate the PINS for the line
        # only positive values, but keeping them signed is good for subtraction
        self.pins = np.zeros((self.num_corners, 2), dtype=np.int16)
        theta = 2 * pi / self.num_corners
        for i in range(self.num_corners):
            self.pins[i, 0] = floor(cos(theta * i) * self.radius) + self.radius + 1
            self.pins[i, 1] = floor(sin(theta * i) * self.radius) + self.radius + 1
        initlog.debug(f"Pin 1 {self.pins[1]}")

        ######################################################################
        # initialize LINE
        self.line = []
        # random first pin
        self.line.append(randint(0, self.num_corners - 1))
        # first line is always a diameter
        self.add_segment((self.line[0] + self.num_corners // 2) % self.num_corners)

    def generate_line(self):
        """Add segments until max_line_len is reached

        Or until a fancier stopping condition is met, eg no improvement on loss
        """
        genlilog = logging.getLogger(f"{self.__class__.__name__}.console.genlilog")
        genlilog.setLevel("INFO")

        #  count = 1
        #  step = self.max_line_len // 80
        #  print(f"000%", end="", flush=True)

        for i in range(1, self.max_line_len):
            genlilog.debug(f"Doing segment {i}")

            next_pin = self.find_next_pin()

            if next_pin == -1:
                genlilog.warn(f"Breaking at segment {i}, no next_pin found")
                break

            genlilog.debug(f"Done segment {i}, found pin {next_pin}")
            self.add_segment(next_pin)

            #  if count % (step // 10 + 1) == 0:
                #  percent = round(count / self.max_line_len * 100)
                #  print("\b\b\b\b", end="", flush=True)
                #  print(f"{percent:03}%", end="", flush=True)
            #  count += 1

        #  print("\b\b\b\bDone.")

    def find_next_pin(self):
        """Find the next pin that has highest residual along the line

        Weigh the probabilities with line len
        """
        findlog = logging.getLogger(f"{self.__class__.__name__}.console.findlog")
        #  findlog.setLevel("DEBUG")
        findlog.setLevel("INFO")

        start_pin = self.line[-1]
        findlog.debug(f"Start_pin {start_pin} Line[-2] {self.line[-2]}")

        probs = []
        for i in range(self.num_corners):
            findlog.log(5, f"Examining pin {i}")
            if i == self.line[-1] or i == self.line[-2]:
                probs.append(0)
                continue

            line_mask, _, line_length = self.get_line_mask(start_pin, i)
            img_res_masked = np.bitwise_and(
                self.img_residual, self.img_residual, where=line_mask
            )

            res_along_line = np.sum(img_res_masked)
            # if adding this line does more harm than good, ignore it
            if res_along_line > 0:
                probs.append(res_along_line / line_length)
            else:
                probs.append(0)

        # if no good line has been found, signal it to generate_line
        if sum(probs) == 0:
            return -1

        findlog.log(5, f"Probs {probs}")

        next_pin = choices(range(self.num_corners), weights=probs, k=1)[0]
        #  findlog.info(f"next_pin {next_pin}")

        return next_pin

    def add_segment(self, end_pin):
        """Add a segment from line[-1] to end_pin

        Update img_built and img_residual
        """
        addseglog = logging.getLogger(f"{self.__class__.__name__}.console.addseglog")
        addseglog.setLevel("INFO")

        addseglog.debug(f"Adding segment from {self.line[-1]} to {end_pin}")

        _, line_mask_weighted, _ = self.get_line_mask(self.line[-1], end_pin)

        self.line.append(end_pin)

        # TODO check if using where=line_mask is faster
        self.img_built = self.img_built + line_mask_weighted
        self.img_residual = self.img_residual - line_mask_weighted

    def get_line_mask(self, start_pin, end_pin):
        """Returns the line_mask, line_mask_weighted and line_length
        """
        getlinelog = logging.getLogger(f"{self.__class__.__name__}.console.getlinelog")
        #  getlinelog.setLevel("DEBUG")
        getlinelog.setLevel("INFO")

        #  getlinelog.debug(f"Getting line from {start_pin} to {end_pin}")

        if end_pin < start_pin:
            start_pin, end_pin = end_pin, start_pin
            #  getlinelog.debug(f"Swapped {start_pin} to {end_pin}")

        seg = start_pin, end_pin
        #  getlinelog.debug(f"Ordered segment {seg}")

        p1 = self.pins[start_pin]
        p2 = self.pins[end_pin]
        #  getlinelog.debug(f"p1 {p1} p2 {p2}")
        line_length = max(abs(p1 - p2))
        #  getlinelog.debug(f"line_length {line_length}")
        getlinelog.debug(f"p[{start_pin}]: {p1} p[{end_pin}]: {p2} len {line_length}")

        # if the line is unknown, compute it
        if not seg in self.line_mask:
            # create the empty mask
            self.line_mask[seg] = np.zeros_like(self.img_objective, dtype=bool)

            # compute the line
            for x, y in bresenham_generator(*p1, *p2):
                self.line_mask[seg][x, y] = True
            # reset the last point
            self.line_mask[seg][x, y] = False

            # compute the weighted line
            self.line_mask_weighted[seg] = (
                self.line_mask[seg].astype(np.int16) * self.line_weight
            )

        # now the value is there
        return self.line_mask[seg], self.line_mask_weighted[seg], line_length

    def save_img_built(self):
        """Save the generated image in path_output
        """
        self.img_result = self.img_built.astype(np.uint8)
        print(f"max {np.max(self.img_result)}")
        cv2.imshow("Result image", self.img_result)
        cv2.imwrite(self.path_output, self.img_result)
        cv2.waitKey(0)

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
