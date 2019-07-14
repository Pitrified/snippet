import cv2
import logging
import numpy as np
import numpy.ma as ma

from timeit import default_timer as timer

from bresenham_generator import bresenham_generator
from line_drawer_creator import Liner


class LinerTest(Liner):

    liner_test_class_logger_loaded = False

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
        super(LinerTest, self).__init__(
            path_input, path_output, num_corners, output_size, max_line_len, line_weight
        )

        self.setup_class_logger()
        initlog = logging.getLogger(f"{self.__class__.__name__}.console.init")
        #  initlog.setLevel("INFO")
        initlog.setLevel("DEBUG")

    def benchmark_bresenham_naive(self):
        """Sum values along a line
        """
        benchlog = logging.getLogger(f"{self.__class__.__name__}.console.bench_bnp")
        benchlog.setLevel("DEBUG")
        #  benchlog.setLevel("INFO")

        p1 = self.pins[0]
        p2 = self.pins[50]

        benchlog.debug(f"p1 {p1} p2 {p2}")

        #  img_built = np.zeros_like(self.img_masked)
        img_built = np.random.normal(loc=0, scale=500, size=self.img_masked.shape)
        img_built = img_built.astype(np.uint16)

        sta_line = timer()

        delta_line = 0
        for x, y in bresenham_generator(*p1, *p2):
            #  benchlog.debug(f"x {x} y {y}")

            # THIS raises RuntimeWarning: overflow encountered
            delta_line += self.img_masked[x, y] - img_built[x, y]

            #  delta_line += np.subtract(
            #  self.img_masked[x, y], img_built[x, y], dtype=np.int16
            #  )

            #  delta_line += int(self.img_masked[x, y]) - img_built[x, y]

        end_line = timer()

        benchlog.debug(f"delta_line {delta_line}")

        tot_time = end_line - sta_line
        benchlog.info(f"time diff along line\t{tot_time:.9f} s")

    def benchmark_bresenham_mask(self):
        """Sum along the line, but using a where mask
        """
        benchlog = logging.getLogger(f"{self.__class__.__name__}.console.bench_bnp")
        #  benchlog.setLevel("DEBUG")
        benchlog.setLevel("INFO")

        p1 = self.pins[0]
        p2 = self.pins[5]
        benchlog.debug(f"p1 {p1} p2 {p2}")

        img_built = np.random.normal(loc=500, scale=500, size=self.img_masked.shape)
        img_built = img_built.astype(np.uint16)

        t1 = timer()

        line_mask = np.zeros_like(self.img_masked, dtype=bool)
        for x, y in bresenham_generator(*p1, *p2):
            line_mask[x, y] = True

        t2 = timer()

        img_delta = np.subtract(
            self.img_masked, img_built, where=line_mask, dtype=np.int16
        )

        t3 = timer()

        benchlog.info(f"time to create linemask\t{t2-t1:.9f} s")
        benchlog.info(f"time to subtract masked\t{t3-t2:.9f} s")

    def benchmark_np_sum(self):
        """Performance for a matrix sum/subtraction
        """

        benchlog = logging.getLogger(f"{self.__class__.__name__}.console.bench_bnp")
        #  benchlog.setLevel("TRACE")
        #  benchlog.setLevel("DEBUG")
        benchlog.setLevel("INFO")

        t1 = timer()
        img_built = np.random.normal(loc=0, scale=500, size=self.img_masked.shape)
        img_built = img_built.astype(np.uint16)
        t2 = timer()

        img_residual = self.img_masked - img_built
        #  img_residual = np.subtract(self.img_masked, img_built, dtype=np.int16)

        t3 = timer()

        benchlog.debug(f"img_res shape {img_residual.shape} dtype {img_residual.dtype}")
        benchlog.log(5, f"normal\n{img_built[0:10, 0:10]}")

        benchlog.debug(f"time generate normal\t{t2-t1:.9f} s")
        benchlog.info(f"time to subtract\t{t3-t2:.9f} s")

    def analyze_drawing(self):
        """Show several linez, benchmark some more
        """
        analog = logging.getLogger(f"{self.__class__.__name__}.console.analog")
        analog.setLevel("DEBUG")
        #  analog.setLevel("INFO")

        #  analog.info(f"img_masked\n{self.img_masked}")

        pinz = np.zeros_like(self.img_masked)
        for pin in self.pins:
            pinz[pin[0], pin[1]] = 1
        #  analog.info(f"pinz\n{pinz}")

        p1 = self.pins[0]
        p2 = self.pins[4]
        analog.debug(f"p1 {p1} p2 {p2}")
        line_length = max(abs(p1 - p2))
        analog.info(f"line_length {line_length}")

        t1 = timer()
        line_img_1 = np.zeros_like(self.img_masked, dtype=np.int16)
        for x, y in bresenham_generator(*p1, *p2):
            line_img_1[x, y] = self.line_weight
        line_img_1[x, y] -= self.line_weight
        t2 = timer()
        analog.info(f"time to create lineimg\t{t2-t1:.9f} s")

        t1a = timer()
        line_mask = np.zeros_like(self.img_masked, dtype=bool)
        for x, y in bresenham_generator(*p1, *p2):
            line_mask[x, y] = True
        line_mask[x, y] = False
        t2a = timer()
        analog.info(f"time to create linemask\t{t2a-t1a:.9f} s")
        analog.debug(f"line_mask\n{line_mask}")

        t3 = timer()
        line_img = line_mask.astype(np.int16)
        #  line_img = line_mask.astype(np.int16) * self.line_weight
        t4 = timer()
        analog.info(f"time to cast linemask\t{t4-t3:.9f} s")
        analog.info(f"total linimg creation\t{t4-t3+(t2a-t1a):.9f} s")
        analog.debug(f"line_img\n{line_img}")

        img_built = np.zeros_like(self.img_masked)

        t5 = timer()
        img_built = img_built + line_img * self.line_weight
        #  img_built = img_built + line_img
        #  img_built = np.add(img_built, line_img)
        t6 = timer()
        analog.info(f"time to mult and sum\t{t6-t5:.9f} s")
        analog.debug(f"img_built\n{img_built}")

        t7 = timer()
        img_delta = np.subtract(
            self.img_masked, img_built, where=line_mask, dtype=np.int16
        )
        t8 = timer()
        analog.info(f"time to subtract mask\t{t8-t7:.9f} s")

        t7 = timer()
        img_delta = np.subtract(self.img_masked, img_built, dtype=np.int16)
        t8 = timer()
        analog.info(f"time to subtract all\t{t8-t7:.9f} s")
        analog.debug(f"img_delta\n{img_delta}")

        t9 = timer()
        img_delta_masked = np.bitwise_and(img_delta, img_delta, where=line_mask)
        t10 = timer()
        analog.info(f"time to mask delta\t{t10-t9:.9f} s")
        analog.info(f"img_delta_masked\n{img_delta_masked}")

        t11 = timer()
        sum_along_line = np.sum(img_delta_masked)
        t12 = timer()
        analog.info(f"time to sum delta\t{t12-t11:.9f} s")
        analog.info(f"sum_along_line: {sum_along_line}")

        t13 = timer()
        not_line_mask = np.bitwise_not(line_mask)
        t14 = timer()
        analog.info(f"time to invert mask\t{t14-t13:.9f} s")

        t15 = timer()
        ma_delta = ma.masked_array(img_delta, mask=not_line_mask)
        sum_along_line = sum(ma_delta)
        t16 = timer()
        analog.info(f"time to sum marray\t{t16-t15:.9f} s")

    def get_str_mat(self, mat, formatter=""):
        """Returns the string of a mat, each element formatted accordingly
        """
        fmt = "{{i{f}}}".format(f=formatter)
        mat_str = ""
        for row in mat:
            for elem in row:
                mat_str += fmt.format(i=elem)
            mat_str += "\n"
        return mat_str

    def setup_class_logger(self):
        """Setup a class wide logger
        """
        # this is run only the first time
        if LinerTest.liner_test_class_logger_loaded is False:
            self.clalog = logging.getLogger(f"{self.__class__.__name__}.console")
            self.clalog.propagate = False

            self.clalog.setLevel("DEBUG")

            module_console_handler = logging.StreamHandler()

            #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
            log_format_module = "%(message)s"
            #  log_format_module = '%(levelname)s: %(message)s'
            formatter = logging.Formatter(log_format_module)
            module_console_handler.setFormatter(formatter)

            self.clalog.addHandler(module_console_handler)

            logging.addLevelName(5, "TRACE")

            #  self.clalog.setLevel('TRACE')
            #  self.clalog.log(5, 'does this work')

            LinerTest.liner_test_class_logger_loaded = True
