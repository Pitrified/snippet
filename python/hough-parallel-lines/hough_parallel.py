import logging
import math
import numpy as np  # type: ignore

from utils import dist_2D


class HoughParallel:
    def __init__(
        self,
        data_x,
        data_y,
        corridor_width,
        r_stride,
        r_min_dist,
        r_max_dist,
        th_bin_num,
    ):
        """Setup the analyzer
        """
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start __init__")

        self.data_x = data_x
        self.data_y = data_y
        self.corridor_width = corridor_width
        self.r_stride = r_stride
        self.r_min_dist = r_min_dist
        self.r_max_dist = r_max_dist

        # the number of bin for theta values must be even
        if th_bin_num % 2 != 0:
            th_bin_num += 1
            logg.warn(f"Changed to even th_bin_num: {th_bin_num}")
        self.th_bin_num = th_bin_num
        self.th_bin_num_half = th_bin_num // 2

        # all the values of possible rotations of the corridor
        self.th_values = np.linspace(0, math.pi, self.th_bin_num, endpoint=False)
        # precompute all the shifts of length corridor_width
        self.shift_val_x = np.cos(self.th_values) * self.corridor_width
        self.shift_val_y = np.sin(self.th_values) * self.corridor_width

    def find_parallel_lines_mat(self):
        """Runs the algorithm on the current values
        """
        # logg = logging.getLogger(f"c.{__name__}.find_parallel_lines_mat")
        # logg.debug(f"Start find_parallel_lines_mat")

        self.compute_all_dist_all_th_mat()

        self.fill_bins()

        self.find_best_params()

        return self.best_th, self.best_r

    def compute_all_dist_all_th_mat(self):
        """Computes the distances for all points and all rotations
        """
        # logg = logging.getLogger(f"c.{__name__}.compute_all_dist_all_th_mat")
        # logg.debug(f"Start compute_all_dist_all_th_mat")

        # distance from all points to the origin
        all_PL_dist = np.sqrt(np.square(self.data_x) + np.square(self.data_y))

        # direction from all points to origin
        all_PL_rad = np.arctan2(self.data_y, self.data_x)

        # use broadcasting to stretch the arrays into common shapes
        # https://numpy.org/devdocs/user/theory.broadcasting.html#figure-4
        all_rel_PL_rad = self.th_values[:, np.newaxis] - all_PL_rad

        cos_all_rel_PL_rad = np.cos(all_rel_PL_rad)

        # distances when considering the point on the left line
        self.all_dist_all_th_l = np.multiply(all_PL_dist, cos_all_rel_PL_rad)
        self.all_dist_all_th_l = self.all_dist_all_th_l.transpose()

        # the distances when considering the point on the right are reduced by corridor width
        self.all_dist_all_th_r = self.all_dist_all_th_l - self.corridor_width
        # logg.debug(f"self.all_dist_all_th_l.shape: {self.all_dist_all_th_l.shape}")
        self.all_dist_all_th = np.vstack(
            (self.all_dist_all_th_l, self.all_dist_all_th_r)
        )
        # logg.debug(f"self.all_dist_all_th.shape: {self.all_dist_all_th.shape}")

    def fill_bins(self):
        """Count the lines found
        """
        # logg = logging.getLogger(f"c.{__name__}.fill_bins")
        # logg.debug(f"Start fill_bins")

        # quantize the dist values along r_stride grid
        self.quant_all_dist_all_th = self.all_dist_all_th / self.r_stride
        self.int_all_dist_all_th = np.rint(self.quant_all_dist_all_th).astype(np.int16)

        self.r_min = np.min(self.int_all_dist_all_th)
        self.r_max = np.max(self.int_all_dist_all_th)
        self.r_bin_num = self.r_max - self.r_min + 1
        # logg.debug(f"r_min: {self.r_min} r_max {self.r_max} r_bin_num {self.r_bin_num}")
        self.bins = np.zeros((self.th_bin_num, self.r_bin_num), dtype=np.uint16)
        # bin 0 is associated with value r_min, 1 with r_min + r_stride and so on

        # transpose the data to easily access by theta
        self.int_all_th_all_dist = self.int_all_dist_all_th.T
        for i_th, all_dist_th in enumerate(self.int_all_th_all_dist):
            # get unique values and their counts
            uniques, counts = np.unique(all_dist_th, return_counts=True)
            for i_u, u in enumerate(uniques):
                i_r = u - self.r_min
                self.bins[i_th][i_r] += counts[i_u]

            # recap = f"all_dist_th.shape: {all_dist_th.shape}"
            # recap += f" u.shape {u.shape}"
            # logg.debug(recap)

    def find_best_params(self):
        """Finds the most frequent line
        """
        # logg = logging.getLogger(f"c.{__name__}.find_best_params")
        # logg.debug(f"Start find_best_params")

        # find the max
        # max_bin = np.max(self.bins)
        argmax_bin = np.argmax(self.bins)
        ind_argmax = np.unravel_index(argmax_bin, self.bins.shape)
        # recap = f"max_bin: {max_bin}"
        # recap += f" argmax_bin: {argmax_bin}"
        # recap += f" ind_argmax: {ind_argmax}"
        # logg.debug(recap)

        # go from index to value
        max_val = ind_argmax[1] + self.r_min
        self.best_r = max_val * self.r_stride
        self.best_th = self.th_values[ind_argmax[0]]

    def compute_all_dist_all_th(self):
        """Computes the distances for all points and all rotations
        """
        logg = logging.getLogger(f"c.{__name__}.compute_all_dist_all_th")
        logg.debug(f"Start compute_all_dist_all_th")

        self.all_dist_all_th_l = []
        self.all_dist_all_th_r = []

        for i_pt in range(self.data_x.shape[0]):
            dist_all_th_left, dist_all_th_right = self.compute_dist_all_th(i_pt)
            self.all_dist_all_th_l.append(dist_all_th_left)
            self.all_dist_all_th_r.append(dist_all_th_right)

        return 0, 0

    def compute_dist_all_th(self, i_line):
        """Computes the distances for a single point and all rotations
        """
        logg = logging.getLogger(f"c.{__name__}.compute_dist_all_th")
        logg.setLevel("INFO")
        logg.debug(f"Start compute_dist_all_th")

        line_x = self.data_x[i_line]
        line_y = self.data_y[i_line]
        logg.debug(f"line_x: {line_x} line_y {line_y}")

        # distance for left side of the corridor (the principal one)
        dist_all_th_left = np.zeros_like(self.th_values)
        # distance for right side of the corridor
        dist_all_th_right = np.zeros_like(self.th_values)

        # for each theta value
        for i_th, th in enumerate(self.th_values):
            logg.debug(f"Start i_th: {i_th} th {math.degrees(th):.0f}")
            # find the distance of this line from the origin
            dist_all_th_left[i_th] = self.dist_line_point(line_x, line_y, th)

            s_x = self.shift_val_x[i_th]
            s_y = self.shift_val_y[i_th]
            logg.debug(f"\ts_x {s_x:.6f} s_y {s_y:.6f}")
            # dist_all_th_right[i_th] = self.dist_line_point(line_x, line_y, th, s_x, s_y)
            dist_all_th_right[i_th] = self.dist_line_point(
                line_x - s_x, line_y - s_y, th
            )

        # self.visual_test_dist_all_th(dist_all_th_left, dist_all_th_right)
        return dist_all_th_left, dist_all_th_right

    def dist_line_point(self, l_x, l_y, l_rad, orig_x=0, orig_y=0):
        r"""Computes the distance between a line and a point

        Note that l_rad is perpendicular to the line, and is the angle between the x
        axis and PT. |PT| is |PL|*cos(TPL), and TPL = TPx - LPx = l_rad - PL_rad.

               y
               |   - _
               |       - _   T
               |           - _
               |             / - _ L
               |            /    . - _
               |           /   .       - _
               |          /  .
               |         / .
               |        /.
               |       .
               |      P
               o-----------------------> x

               y
               |
               |
               |                     L
               |                   _
               |               _ -.
               |           _ -  .
               |    T  _ -    .
               |   _ -      .
               |      \  .
               |       .
               |      P
               o-----------------------> x
        """
        # find the direction PL
        PL_rad = math.atan2(l_y - orig_y, l_x - orig_x)
        # find the angle between line and PL
        # rel_PL_rad = l_rad - PL_rad
        rel_PL_rad = PL_rad - l_rad
        # the distance between L and P
        PL_dist = dist_2D(l_x, l_y, orig_x, orig_y)
        # distance from line l to P
        dist = PL_dist * math.cos(rel_PL_rad)

        logg = logging.getLogger(f"c.{__name__}.dist_line_point")
        logg.setLevel("INFO")
        # recap = f"PL_rad: {PL_rad:.6f}"
        recap = f"PL_rad: {math.degrees(PL_rad):.0f}"
        # recap += f" rel_PL_rad {rel_PL_rad:.6f}"
        recap += f" rel_PL_rad: {math.degrees(rel_PL_rad):.0f}"
        recap += f" PL_dist {PL_dist:.6f}"
        recap += f" dist {dist:.6f}"
        logg.debug(recap)

        return dist
