import logging

from pathlib import Path
from typing import cast, Optional, Literal, Dict
from cursive_writer.utils.type_utils import Spline, ThickSpline

from cursive_writer.utils.utils import load_spline
from cursive_writer.spliner.spliner import compute_long_thick_spline


class Letter:
    def __init__(
        self,
        letter: str,
        left_type: Literal["high_down", "high_up", "low_up"],
        right_type: Literal["high_up", "low_up"],
        pf_spline_alone: Optional[Path] = None,
        pf_spline_high: Optional[Path] = None,
        pf_spline_low: Optional[Path] = None,
        thickness: int = 10,
    ):
        """TODO: what is __init__ doing?

        right_type and left_type are referred to the natural state of the letter:
        high/low indicate the height of the attachment, up/down indicate the concavity

        all letters with left_type low_up also have the alternative version high_up

              possible types:
                    left_type          right_type

                    high_down
                      high_up          high_up
                               letter
                       low_up          low_up

        """
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start __init__ {letter}")

        if pf_spline_alone is None and pf_spline_low is None and pf_spline_high is None:
            logg.error(f"No file specified")

        self.letter = letter
        self.right_type = right_type
        self.left_type = left_type
        self.thickness = thickness

        self.pf_spline: Dict[str, Optional[Path]] = {}
        self.pf_spline["alone"] = pf_spline_alone
        self.pf_spline["high"] = pf_spline_high
        self.pf_spline["low"] = pf_spline_low

        self.spline_seq: Dict[str, Spline] = {}
        self.spline_thick_samples: Dict[str, ThickSpline] = {}
        self.gly_num: Dict[str, int] = {}
        self.point_num: Dict[str, int] = {}

        # if available, load alternate high splines
        if self.pf_spline["alone"] is not None:
            self.data_dir = self.pf_spline["alone"].parent
            self.load_spline_info("alone")
        if self.pf_spline["high"] is not None:
            self.data_dir = self.pf_spline["high"].parent
            self.load_spline_info("high")
        if self.pf_spline["low"] is not None:
            self.data_dir = self.pf_spline["low"].parent
            self.load_spline_info("low")

    def load_spline_info(self, which: str) -> None:
        """TODO: what is load_spline_info doing?
        """
        logg = logging.getLogger(f"c.{__name__}.load_spline_info")
        # logg.debug(f"Start load_spline_info {which}")

        self.spline_seq[which] = load_spline(
            cast(Path, self.pf_spline[which]), self.data_dir
        )
        self.spline_thick_samples[which] = compute_long_thick_spline(
            self.spline_seq[which], self.thickness
        )
        self.gly_num[which] = len(self.spline_seq[which])
        self.point_num[which] = sum(map(len, self.spline_seq[which]))

        # check that there is a left glyph, a main spline and a right one
        if self.gly_num[which] <= 2:
            logg.warn(f"Not enough glyphs in the spline '{which}'")

    def get_pf(self, which: str) -> Path:
        """TODO: what is get_pf doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.get_pf")
        # logg.debug(f"Start get_pf")
        valid_which = self.get_valid_type(which)
        return cast(Path, self.pf_spline[valid_which])

    def get_spline_seq(self, which: str) -> Spline:
        """TODO: what is get_spline_seq doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.get_spline_seq")
        # logg.debug(f"Start get_spline_seq")
        valid_which = self.get_valid_type(which)
        return self.spline_seq[valid_which]

    def get_thick_samples(self, which: str) -> ThickSpline:
        """TODO: what is get_thick_samples doing?
        """
        # logg = logging.getLogger(f"c.{__name__}.get_thick_samples")
        # logg.debug(f"Start get_thick_samples")
        valid_which = self.get_valid_type(which)
        return self.spline_thick_samples[valid_which]

    def get_valid_type(self, which: str) -> str:
        """TODO: what is get_valid_type doing?
        """
        logg = logging.getLogger(f"c.{__name__}.get_valid_type")

        # the requested type exists
        if self.pf_spline[which] is not None:
            return which

        # fallback to some other option
        if which == "high":
            if self.pf_spline["alone"] is not None:
                logg.warn(f"Missing data for {self.letter}: '{which}' - return 'alone'")
                return "alone"
            if self.pf_spline["low"] is not None:
                logg.warn(f"Missing data for {self.letter}: '{which}' - return 'low'")
                return "low"

        if which == "low":
            if self.pf_spline["alone"] is not None:
                logg.warn(f"Missing data for {self.letter}: '{which}' - 'alone'")
                return "alone"
            if self.pf_spline["high"] is not None:
                logg.warn(f"Missing data for {self.letter}: '{which}' - return 'high'")
                return "high"

        if which == "alone":
            if self.pf_spline["low"] is not None:
                logg.warn(f"Missing data for {self.letter}: '{which}' - return 'low'")
                return "low"
            if self.pf_spline["high"] is not None:
                logg.warn(f"Missing data for {self.letter}: '{which}' - return 'high'")
                return "high"

        # something went wrong
        logg.error(f"Unable to find data for: {which}")
        return "error"

    def __str__(self):
        the_str = f"'{self.letter}'"
        the_str += f" r_type '{self.right_type}' l_type '{self.left_type}'"

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
