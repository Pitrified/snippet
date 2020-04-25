import logging

from cursive_writer.utils.utils import load_spline


class Letter:
    def __init__(
        self,
        letter,
        left_type,
        right_preference,
        pf_spline_alone=None,
        pf_spline_high=None,
        pf_spline_low=None,
    ):
        """TODO: what is __init__ doing?

        right_preference and left_type are referred to the natural state of the letter:
        high/low indicate the height of the attachment, up/down indicate the concavity

        all letters with left_type low_up also have the alternative version high_up
        """
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start __init__ {letter}")

        if pf_spline_alone is None and pf_spline_low is None and pf_spline_high is None:
            logg.error(f"No file specified")

        self.letter = letter
        self.right_preference = right_preference
        self.left_type = left_type

        self.pf_spline = {}
        self.pf_spline["alone"] = pf_spline_alone
        self.pf_spline["high"] = pf_spline_high
        self.pf_spline["low"] = pf_spline_low

        self.spline_seq = {}
        self.gly_num = {}
        self.point_num = {}

        self.data_dir = self.pf_spline["alone"].parent

        # if available, load alternate high splines
        if self.pf_spline["alone"] is not None:
            self.load_spline_info("alone")
        if self.pf_spline["high"] is not None:
            self.load_spline_info("high")
        if self.pf_spline["low"] is not None:
            self.load_spline_info("low")

    def load_spline_info(self, which):
        """TODO: what is load_spline_info doing?
        """
        logg = logging.getLogger(f"c.{__name__}.load_spline_info")
        # logg.debug(f"Start load_spline_info {which}")

        self.spline_seq[which] = load_spline(self.pf_spline[which], self.data_dir)
        self.gly_num[which] = len(self.spline_seq[which])
        self.point_num[which] = 0
        for glyph in self.spline_seq[which]:
            self.point_num[which] += len(glyph)

        # check that there is a left glyph, a main spline and a right one
        if self.gly_num[which] <= 2:
            logg.warn(f"Not enough glyphs in the spline '{which}'")

    def __str__(self):
        the_str = f"'{self.letter}'"
        the_str += f" r_pref '{self.right_preference}' l_type '{self.left_type}'"

        if self.pf_spline["alone"] is not None:
            the_str += f", glyphs_alone {self.gly_num['alone']}"
            the_str += f", points_alone {self.point_num['alone']}"
        if self.pf_spline["high"] is not None:
            the_str += f", glyphs_high {self.gly_num['high']}"
            the_str += f", points_high {self.point_num['high']}"
        if self.pf_spline["low"] is not None:
            the_str += f", glyphs_low {self.gly_num['low']}"
            the_str += f", points_low {self.point_num['low']}"

        return the_str

    def __repr__(self):
        return self.__str__()
