import logging
import math
import numpy as np
import matplotlib.pyplot as plt

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
        """TODO: what is __init__ doing?
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
        # self.visual_test_shift()

    def find_parallel_lines_mat(self):
        """TODO: what is find_parallel_lines_mat doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.find_parallel_lines_mat")
        # logg.debug(f"Start find_parallel_lines_mat")

        # distance from all points to the origin
        all_PL_dist = np.sqrt(np.square(self.data_x) + np.square(self.data_y))

        # direction from all points to origin
        all_PL_rad = np.arctan2(self.data_y, self.data_x)

        # use broadcasting to stretch the arrays into common shapes
        # https://numpy.org/devdocs/user/theory.broadcasting.html#figure-4
        all_rel_PL_rad = self.th_values[:, np.newaxis] - all_PL_rad

        cos_all_rel_PL_rad = np.cos(all_rel_PL_rad)

        self.all_dist_all_th_l = np.multiply(all_PL_dist, cos_all_rel_PL_rad)
        self.all_dist_all_th_l = self.all_dist_all_th_l.transpose()
        self.all_dist_all_th_r = self.all_dist_all_th_l - self.corridor_width
        # logg.debug(f"self.all_dist_all_th_l.shape: {self.all_dist_all_th_l.shape}")
        self.all_dist_all_th = np.vstack(
            (self.all_dist_all_th_l, self.all_dist_all_th_r)
        )
        # logg.debug(f"self.all_dist_all_th.shape: {self.all_dist_all_th.shape}")

        # quantize the dist values along r_stride grid
        self.quant_all_dist_all_th = self.all_dist_all_th / self.r_stride
        self.int_all_dist_all_th = np.rint(self.quant_all_dist_all_th).astype(np.int16)

        r_min = np.min(self.int_all_dist_all_th)
        r_max = np.max(self.int_all_dist_all_th)
        r_bin_num = r_max - r_min + 1
        # logg.debug(f"r_min: {r_min} r_max {r_max} r_bin_num {r_bin_num}")
        self.bins = np.zeros((self.th_bin_num, r_bin_num), dtype=np.uint16)
        # bin 0 is associated with value r_min, 1 with r_min + r_stride and so on

        # transpose the data to easily access by theta
        self.int_all_th_all_dist = self.int_all_dist_all_th.T
        for i_th, all_dist_th in enumerate(self.int_all_th_all_dist):
            # get unique values and their counts
            uniques, counts = np.unique(all_dist_th, return_counts=True)
            for i_u, u in enumerate(uniques):
                i_r = u - r_min
                self.bins[i_th][i_r] += counts[i_u]
                pass

            # recap = f"all_dist_th.shape: {all_dist_th.shape}"
            # recap += f" u.shape {u.shape}"
            # logg.debug(recap)

        return 0, 0

    def find_parallel_lines(self):
        """TODO: what is find_parallel_lines doing?
        """
        logg = logging.getLogger(f"c.{__name__}.find_parallel_lines")
        logg.debug(f"Start find_parallel_lines")

        # self.all_dist_all_th = []
        self.all_dist_all_th_l = []
        self.all_dist_all_th_r = []

        for i_pt in range(self.data_x.shape[0]):
            dist_all_th_left, dist_all_th_right = self.compute_dist_all_th(i_pt)
            self.all_dist_all_th_l.append(dist_all_th_left)
            self.all_dist_all_th_r.append(dist_all_th_right)

        # self.visual_test_all_dist_all_th()

        return 0, 0

    def compute_dist_all_th(self, i_line):
        """TODO: what is compute_dist_all_th doing?
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

            # i_sh = self.index_wrap(i_th + self.th_bin_num_half, self.th_bin_num)
            i_sh = i_th
            s_x = self.shift_val_x[i_sh]
            s_y = self.shift_val_y[i_sh]
            logg.debug(f"\ti_sh: {i_sh} s_x {s_x:.6f} s_y {s_y:.6f}")
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

    def index_wrap(self, index, vec_length):
        """TODO: what is index_wrap doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.index_wrap")
        # logg.debug(f"Start index_wrap")
        if index < 0:
            return index + vec_length
        if index >= vec_length:
            return index - vec_length
        return index

    def visual_test_shift(self):
        """TODO: what is visual_test_shift doing?
        """
        logg = logging.getLogger(f"c.{__name__}.visual_test_shift")
        logg.debug(f"Start visual_test_shift")

        # plot all the shift values
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches((8, 8))
        ax.set_title("Shift test")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        style = {"ls": "", "marker": ".", "color": "k"}
        ax.plot(self.shift_val_x, self.shift_val_y, **style)

    def visual_test_dist_all_th(self, dist_all_th_left, dist_all_th_right):
        """TODO: what is visual_test_dist_all_th doing?
        """
        logg = logging.getLogger(f"c.{__name__}.visual_test_dist_all_th")
        logg.debug(f"Start visual_test_dist_all_th")

        # plot all the shift values
        fig, ax = plt.subplots(1, 1)
        fig.set_size_inches((8, 8))
        ax.set_title("Test dist_all_th")
        ax.set_xlabel("theta")
        ax.set_ylabel("r")

        style = {"ls": "", "marker": ".", "color": "k"}
        ax.plot(self.th_values, dist_all_th_left, **style)
        ax.plot(self.th_values, dist_all_th_right, **style)

    def visual_test_all_dist_all_th(self, ax=None):
        """TODO: what is visual_test_all_dist_all_th doing?
        """
        logg = logging.getLogger(f"c.{__name__}.visual_test_all_dist_all_th")
        logg.debug(f"Start visual_test_all_dist_all_th")

        if ax is None:
            fig, ax = plt.subplots(1, 1)
            fig.set_size_inches((8, 8))
            ax.set_title("Test all_dist_all_th")
            ax.set_xlabel("theta")
            ax.set_ylabel("r")

        style = {"ls": "-", "marker": "", "color": "y"}
        # style = {"ls": "", "marker": ".", "color": "y"}
        for dist_all_th in self.all_dist_all_th_l:
            dist_all_th /= self.r_stride
            ax.plot(self.th_values, dist_all_th, **style)
        style["color"] = "g"
        for dist_all_th in self.all_dist_all_th_r:
            dist_all_th /= self.r_stride
            ax.plot(self.th_values, dist_all_th, **style)

        style = {"ls": "", "marker": ".", "color": "c"}
        for dist_all_th in self.int_all_dist_all_th:
            ax.plot(self.th_values, dist_all_th, **style)

    def visual_test_bins(self, ax=None):
        """TODO: what is visual_test_bins doing?

        matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html
        """
        if ax is None:
            fig, ax = plt.subplots(1, 1)
            fig.set_size_inches((8, 8))
            ax.set_title("Test bins")
            ax.set_xlabel("theta")
            ax.set_ylabel("r")

        im = ax.imshow(self.bins.T)
        return im
        # cbar_kw = {}
        # cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
        # cbarlabel = "Collinear points"
        # cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")


# TODO: heatmap per mostrare quanto pieni sono i bin
