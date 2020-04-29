import logging
import math
import numpy as np  # type: ignore
import matplotlib.pyplot as plt  # type: ignore
from scipy.ndimage import gaussian_filter  # type: ignore

from typing import Tuple, Optional


class DoubleHough:
    def __init__(
        self,
        data_x: np.ndarray,
        data_y: np.ndarray,
        th_bin_num_fp: int,
        r_stride_fp: float,
        th_bin_num_sp: int,
        r_stride_sp: float,
        r_num_sp: int,
        corridor_width: float,
    ):
        """Setup the analyzer
        """
        # logg = logging.getLogger(f"c.{__name__}.__init__")
        # logg.debug(f"Start __init__")

        # points in cartesian space
        self.data_x = data_x
        self.data_y = data_y

        # params for the first sampling pass
        self.r_stride_fp = r_stride_fp
        self.th_bin_num_fp = th_bin_num_fp

        # params for the second sampling pass
        self.r_stride_sp = r_stride_sp
        self.th_bin_num_sp = th_bin_num_sp
        self.r_num_sp = r_num_sp

        # distance between the two lines
        self.corridor_width = corridor_width

        # all the values of possible rotations of the corridor in the first pass
        self.th_values_fp = np.linspace(0, math.pi, self.th_bin_num_fp, endpoint=False)
        self.th_fp_wid = math.radians(180 / self.th_bin_num_fp)
        # logg.debug(f"First th bins are {math.degrees(self.th_fp_wid):.4f} degrees wide")

    def find_parallel_lines(self) -> Tuple[float, float]:
        """Runs the algorithm on the current values
        """
        # logg = logging.getLogger(f"c.{__name__}.find_parallel_lines")
        # logg.debug(f"Start find_parallel_lines")

        # precompute values common to both passes
        self.precompute_values()

        #####################
        # do the first pass #
        #####################

        # # use some prior knowledge on the orientation of the corridor
        # self.th_values_fp = np.linspace(
        #     math.pi * 2 / 5, math.pi * 3 / 5, self.th_bin_num_fp, endpoint=False
        # )

        # # compute the distances
        # all_dist_fp_th = self.compute_all_dist_from_th_mat(self.th_values_fp)
        # # fill the bins
        # bins_fp, r_min_fp = self.fill_bins(
        #     all_dist_fp_th, self.th_bin_num_fp, self.r_stride_fp
        # )
        # # find the max
        # best_th_fp, best_r_fp = self.find_max(
        #     bins_fp, r_min_fp, self.r_stride_fp, self.th_values_fp
        # )
        best_th_fp = math.radians(90)
        best_r_fp = -0.28
        # logg.debug(f"best_th_fp: {best_th_fp} best_r_fp {best_r_fp}")
        print(f"best_th_fp: {best_th_fp} best_r_fp {best_r_fp}")

        ######################
        # do the second pass #
        ######################

        # compute the th values for the precise interval
        self.th_values_sp = np.linspace(
            best_th_fp - self.th_fp_wid * 2,
            best_th_fp + self.th_fp_wid * 2,
            self.th_bin_num_sp,
        )
        # logg.debug(f"th_values_sp.shape: {self.th_values_sp.shape}")
        # logg.debug(f"th_values_sp deg: {np.degrees(self.th_values_sp)}")

        # compute the distances
        self.all_dist_sp_th = self.compute_all_dist_from_th_mat(self.th_values_sp)

        # fill the bins
        self.bins_sp, r_min_sp = self.fill_bins(
            self.all_dist_sp_th,
            self.th_bin_num_sp,
            self.r_stride_sp,
            best_r_fp,
            self.r_num_sp,
        )

        # smooth the bins
        self.smooth_bins_sp = gaussian_filter(self.bins_sp, 1)

        # find the max
        best_th_sp, best_r_sp = self.find_max(
            self.smooth_bins_sp, r_min_sp, self.r_stride_sp, self.th_values_sp
        )

        print(f"best_th_sp: {best_th_sp} best_r_sp {best_r_sp}")

        return best_th_sp, best_r_sp

    def precompute_values(self):
        """TODO: what is precompute_values doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.precompute_values")
        # logg.debug(f"Start precompute_values")

        # distance from all points to the origin
        self.all_OL_dist = np.sqrt(np.square(self.data_x) + np.square(self.data_y))

        # direction from all points to origin
        self.all_OL_rad = np.arctan2(self.data_y, self.data_x)

    def compute_all_dist_from_th_mat(self, th_values: np.ndarray) -> np.ndarray:
        """Computes the distances for all points and all given rotations values
        """
        # logg = logging.getLogger(f"c.{__name__}.compute_all_dist_from_th_mat")
        # logg.debug(f"Start compute_all_dist_from_th_mat")

        # use broadcasting to stretch the arrays into common shapes
        # https://numpy.org/devdocs/user/theory.broadcasting.html#figure-4
        # the angle between the origin and the point, and the line
        all_rel_OL_rad = th_values[:, np.newaxis] - self.all_OL_rad

        cos_all_rel_OL_rad = np.cos(all_rel_OL_rad)

        # distances when considering the point on the left line
        all_dist_from_th_l = np.multiply(self.all_OL_dist, cos_all_rel_OL_rad)
        all_dist_from_th_l = all_dist_from_th_l.transpose()

        # the distances when considering the point on the right are reduced by corridor width
        all_dist_from_th_r = all_dist_from_th_l - self.corridor_width
        # logg.debug(f"all_dist_from_th_l.shape: {all_dist_from_th_l.shape}")

        # stack the two sets of sinusoids
        all_dist_from_th = np.vstack((all_dist_from_th_l, all_dist_from_th_r))
        # logg.debug(f"all_dist_from_th.shape: {all_dist_from_th.shape}")
        return all_dist_from_th

    def fill_bins(
        self,
        all_dist_from_th: np.ndarray,
        th_bin_num: int,
        r_stride: float,
        r_central: Optional[float] = None,
        r_num_sp: Optional[int] = None,
    ) -> Tuple[np.ndarray, float]:
        """TODO: what is fill_bins doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.fill_bins")
        # logg.debug(f"Start fill_bins")
        # logg.debug(f"min {np.min(all_dist_from_th)} max {np.max(all_dist_from_th)}")

        # quantize the dist values along r_stride grid by zooming in and rounding
        quant_all_dist_from_th = all_dist_from_th / r_stride
        int_all_dist_from_th = np.rint(quant_all_dist_from_th)

        # filter int_all_th_all_dist
        if r_central is not None and r_num_sp is not None:
            # the extremes in the regular coord
            r_sup = r_central + r_num_sp * r_stride
            r_inf = r_central - r_num_sp * r_stride
            # logg.debug(f"r_sup: {r_sup} r_inf {r_inf}")
            # the extremes in the translated coord
            int_r_sup = int(np.rint(r_sup / r_stride))
            int_r_inf = int(np.rint(r_inf / r_stride))
            # logg.debug(f"int_r_sup: {int_r_sup} int_r_inf {int_r_inf}")

            # as we use NaNs, this is cast to float
            int_all_dist_from_th = np.where(
                np.logical_and(
                    np.less_equal(int_all_dist_from_th, int_r_sup),
                    np.greater_equal(int_all_dist_from_th, int_r_inf),
                ),
                int_all_dist_from_th,
                np.nan,
            )

            # save a bunch of info for plotting
            self.int_r_sup = int_r_sup
            self.int_r_inf = int_r_inf
            self.quant_all_dist_from_th = quant_all_dist_from_th
            # self.int_all_dist_from_th = int_all_dist_from_th

        # find the extremes of the distance interval
        r_min = np.nanmin(int_all_dist_from_th)
        int_r_min = int(r_min)
        self.int_r_min = int_r_min
        r_max = np.nanmax(int_all_dist_from_th)
        r_bin_num = int(r_max - r_min + 1)
        # logg.debug(f"r_min: {r_min} r_max {r_max} r_bin_num {r_bin_num}")

        bins = np.zeros((th_bin_num, r_bin_num), dtype=np.uint32)
        # bin 0 is associated with value r_min, 1 with r_min + r_stride and so on
        # logg.debug(f"bins.shape: {bins.shape}")

        # transpose the data to easily access by theta
        int_from_th_all_dist = int_all_dist_from_th.T
        for i_th, all_dist_th in enumerate(int_from_th_all_dist):
            # get unique values and their counts
            # avoid nan values
            uniques, counts = np.unique(
                all_dist_th[~np.isnan(all_dist_th)], return_counts=True
            )
            # cast uniques back to int
            uniques = uniques.astype(np.int32)
            for i_u, u in enumerate(uniques):
                i_r = u - int_r_min
                bins[i_th][i_r] += counts[i_u]

        return bins, r_min

    def find_max(
        self, bins: np.ndarray, r_min: float, r_stride: float, th_values: np.ndarray
    ) -> Tuple[float, float]:
        """TODO: what is find_max doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.find_max")
        # logg.debug(f"Start find_max")

        # max_bin = np.max(bins)
        argmax_bin = np.argmax(bins)
        ind_argmax = np.unravel_index(argmax_bin, bins.shape)
        # recap = f"max_bin: {max_bin}"
        # recap += f" argmax_bin: {argmax_bin}"
        # recap += f" ind_argmax: {ind_argmax}"
        # logg.debug(recap)

        # go from index to value
        max_val = ind_argmax[1] + r_min
        best_r = max_val * r_stride
        best_th = th_values[ind_argmax[0]]

        return best_th, best_r


class VisualDoubleHough(DoubleHough):
    def __init__(
        self,
        data_x: np.ndarray,
        data_y: np.ndarray,
        th_bin_num_fp: int,
        r_stride_fp: float,
        th_bin_num_sp: int,
        r_stride_sp: float,
        r_num_sp: int,
        corridor_width: float,
    ):
        """Setup the analyzer
        """
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start __init__")

        super().__init__(
            data_x,
            data_y,
            th_bin_num_fp,
            r_stride_fp,
            th_bin_num_sp,
            r_stride_sp,
            r_num_sp,
            corridor_width,
        )

    def visual_test_all_dist_sp_th(self, ax=None):
        """TODO: what is visual_test_all_dist_sp_th doing?
        """
        logg = logging.getLogger(f"c.{__name__}.visual_test_all_dist_sp_th")
        logg.debug(f"Start visual_test_all_dist_sp_th")

        if ax is None:
            fig, ax = plt.subplots(1, 1)
            fig.set_size_inches((8, 8))
            ax.set_title("Test all_dist_sp_th")
            ax.set_xlabel("theta")
            ax.set_ylabel("r")

        style = {"ls": "-", "marker": "", "color": "y"}
        # style = {"ls": "", "marker": ".", "color": "y"}

        # for dist_all_th in self.all_dist_sp_th:
        #     ax.plot(self.th_values_sp, dist_all_th, **style)

        quant_all_dist_from_th = np.where(
            np.logical_and(
                np.less_equal(self.quant_all_dist_from_th, self.int_r_sup),
                np.greater_equal(self.quant_all_dist_from_th, self.int_r_inf),
            ),
            self.quant_all_dist_from_th,
            np.nan,
        )
        for dist_all_th in quant_all_dist_from_th:
            dist_all_th *= self.r_stride_sp
            ax.plot(self.th_values_sp, dist_all_th, **style)

    def visual_test_bins_sp(self, which="smooth", ax=None):
        """TODO: what is visual_test_bins_sp doing?
        """
        logg = logging.getLogger(f"c.{__name__}.visual_test_bins_sp")
        logg.debug(f"Start visual_test_bins_sp")

        if ax is None:
            fig, ax = plt.subplots(1, 1)
            fig.set_size_inches((8, 8))

        if which == "smooth":
            im = ax.imshow(self.smooth_bins_sp.T)
        else:
            im = ax.imshow(self.bins_sp.T)

        th_xticks = list(range(0, self.th_values_sp.shape[0], 5))
        th_xticklabels = list(
            [f"{math.degrees(self.th_values_sp[t]):.1f}" for t in th_xticks]
        )
        ax.set_xticks(th_xticks)
        ax.set_xticklabels(th_xticklabels, rotation=45)

        r_yticks = list(range(0, self.bins_sp.shape[1], 5))
        r_yticklabels = list(
            [f"{(t+self.int_r_min)*self.r_stride_sp:.3f}" for t in th_xticks]
        )
        ax.set_yticks(r_yticks)
        ax.set_yticklabels(r_yticklabels, rotation=90)

        ax.invert_yaxis()
        ax.set_title(f"Lines per bin second pass {which}")
        ax.set_xlabel("theta (deg)")
        ax.set_ylabel("r (m)")

        return im
