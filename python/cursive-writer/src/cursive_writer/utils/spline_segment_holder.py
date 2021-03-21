import logging
import copy

from cursive_writer.utils.utils import iterate_double_list
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.spliner.spliner import compute_cubic_segment
from cursive_writer.spliner.spliner import compute_thick_spline


class SplineSegmentHolder:
    def __init__(self, thickness: float = -1) -> None:
        self.cn = self.__class__.__name__
        logg = logging.getLogger(f"c.{self.cn}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        # remember the position used to compute the current segmentes
        # { spid : (x, y, ori_deg) }
        # MAYBE use copy ?
        self.cached_pos = {}

        # dict of segments interpolated
        self.segments = {}

        # how many points per segment
        self.num_samples = 50

        self.thickness = thickness

    def update_data(self, new_all_SP, new_path_SP):
        """TODO: what is update_data doing?
        """
        logg = logging.getLogger(f"c.{self.cn}.update_data")
        # logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('update_data')}")

        logg.log(5, f"new_all_SP: {new_all_SP}")
        logg.log(5, f"new_path_SP: {new_path_SP}")

        full_path = list(iterate_double_list(new_path_SP))

        if len(full_path) == 0:
            logg.warn(f"The path is {fmt_cn('empty', 'alert')}")
            return

        if len(full_path) == 1:
            logg.warn(f"The path has {fmt_cn('one', 'alert')} element")
            spid0 = full_path[0]
            self.cached_pos[spid0] = copy.copy(new_all_SP[spid0])
            logg.log(5, f"self.cached_pos[spid0]: {self.cached_pos[spid0]}")
            logg.log(5, f"id(self.cached_pos[spid0]): {id(self.cached_pos[spid0])}")
            logg.log(5, f"new_all_SP[spid0]: {new_all_SP[spid0]}")
            logg.log(5, f"id(new_all_SP[spid0]): {id(new_all_SP[spid0])}")
            return

        spid0 = full_path[0]
        for spid1 in full_path[1:]:
            pair = (spid0, spid1)
            logg.log(5, f"Processing pair: {pair}")

            # both points already seen
            if spid0 in self.cached_pos and spid1 in self.cached_pos:

                # check if their pos is the same
                if (
                    self.cached_pos[spid0] == new_all_SP[spid0]
                    and self.cached_pos[spid1] == new_all_SP[spid1]
                ):

                    # check if the segment between them is already computed
                    if pair in self.segments:
                        # nothing to recompute
                        logg.log(5, f"Already computed pair: {pair}")

                        # get ready for next iteration
                        spid0 = spid1
                        continue

            # if any of the conditions fail, save the points and recompute the segment
            logg.log(5, f"Now computing pair: {pair}")

            # only update the cached pos of the left point, the right one has
            # to still be wrong in the next iteration, when it will be the left
            # one, and will be corrected
            self.cached_pos[spid0] = copy.copy(new_all_SP[spid0])

            # use the right point from the new data arriving
            self.segments[pair] = self.compute_segment_points(
                self.cached_pos[spid0], new_all_SP[spid1],
            )

            # get ready for next iteration
            spid0 = spid1

        # finally update the last right point
        self.cached_pos[spid1] = copy.copy(new_all_SP[spid1])

        # MAYBE do clean up of unused segments

    def compute_segment_points(self, p0, p1):
        """TODO: what is compute_segment_points doing?

        TODO: do this with multiprocessing
        MAYBE: resample the segment with different precision for different zoom levels?
        """
        logg = logging.getLogger(f"c.{self.cn}.compute_segment_points")
        # logg.setLevel("TRACE")
        logg.log(5, f"Start {fmt_cn('compute_segment_points')} {p0} :: {p1}")

        # if thickness is set, compute the thick spline
        if self.thickness == -1:
            x_segment, y_segment = compute_cubic_segment(p0, p1)
        else:
            logg.log(5, f"self.thickness: {self.thickness}")
            x_segment, y_segment = compute_thick_spline(p0, p1, self.thickness)

        the_points = list(zip(x_segment, y_segment))

        logg.log(5, f"the_points: {the_points}")

        return the_points
