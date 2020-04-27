import logging

from cursive_writer.utils.type_utils import Glyph, Spline


class LigatureInfo:
    def __init__(
        self,
        f_let_type: str,
        s_let_type: str,
        spline_seq_con: Spline,
        f_gly_chop: Glyph,
        s_gly_chop: Glyph,
        shift: float,
    ):
        """TODO: what is __init__ doing?

        TODO: also needs some versioning of the Letter used to build the connection
        """
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start __init__")

        self.f_let_type = f_let_type
        self.s_let_type = s_let_type
        self.spline_seq_con = spline_seq_con
        self.f_gly_chop = f_gly_chop
        self.s_gly_chop = s_gly_chop
        self.shift = shift
