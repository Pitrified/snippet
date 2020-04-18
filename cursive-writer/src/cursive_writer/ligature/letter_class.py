import logging

from cursive_writer.utils.utils import load_spline


class Letter:
    def __init__(
        self, letter, left_type, right_preference, pf_spline, pf_spline_high=None
    ):
        """TODO: what is __init__ doing?

        right_preference and left_type are referred to the natural state of the letter:
        high/low indicate the height of the attachment, up/down indicate the concavity

        all letters with left_type low_up also have the alternative version high_up
        """
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start __init__ {letter}")

        self.letter = letter
        self.right_preference = right_preference
        self.left_type = left_type

        self.pf_spline = {}
        self.pf_spline["reg"] = pf_spline
        self.pf_spline["high"] = pf_spline_high

        self.spline_seq = {}
        self.gly_num = {}
        self.point_num = {}

        self.data_dir = self.pf_spline["reg"].parent

        # load info on principal seq
        self.load_spline_info("reg")
        # if available, load alternate high spline
        if self.pf_spline["high"] is not None:
            self.load_spline_info("high")

    def load_spline_info(self, which):
        """TODO: what is load_spline_info doing?
        """
        logg = logging.getLogger(f"c.{__name__}.load_spline_info")
        logg.debug(f"Start load_spline_info {which}")

        self.spline_seq[which] = load_spline(self.pf_spline[which], self.data_dir)
        self.gly_num[which] = len(self.spline_seq[which])
        self.point_num[which] = 0
        for glyph in self.spline_seq[which]:
            self.point_num[which] += len(glyph)

        if self.gly_num[which] <= 2:
            logg.warn(f"Not enough glyphs in the spline '{which}'")

    def __str__(self):
        the_str = f"'{self.letter}'"
        the_str += f" r_pref '{self.right_preference}' l_type '{self.left_type}'"
        the_str += f", glyphs {self.gly_num['reg']}, points {self.point_num['reg']}"

        if self.pf_spline["high"] is not None:
            the_str += f", glyphs_high {self.gly_num['high']}"
            the_str += f", points_high {self.point_num['high']}"

        return the_str

    def __repr__(self):
        return self.__str__()
