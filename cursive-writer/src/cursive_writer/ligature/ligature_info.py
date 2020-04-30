# import logging

from cursive_writer.utils.type_utils import Glyph, Spline


class LigatureInfo:
    def __init__(
        self,
        f_pf_name: str,
        s_pf_name: str,
        f_let_type: str,
        s_let_type: str,
        spline_seq_con: Spline,
        f_gly_chop: Glyph,
        s_gly_chop: Glyph,
        shift: float,
        f_hash_sha1: str,
        s_hash_sha1: str,
    ):
        """TODO: what is __init__ doing?

        TODO: also needs some versioning of the Letter used to build the connection
        """
        # logg = logging.getLogger(f"c.{__name__}.__init__")
        # logg.debug(f"Start __init__")

        self.f_pf_name = f_pf_name
        self.s_pf_name = s_pf_name
        self.f_let_type = f_let_type
        self.s_let_type = s_let_type
        self.spline_seq_con = spline_seq_con
        self.f_gly_chop = f_gly_chop
        self.s_gly_chop = s_gly_chop
        self.shift = shift
        self.f_hash_sha1 = f_hash_sha1
        self.s_hash_sha1 = s_hash_sha1

    def __str__(self):
        the_str = f"'{self.f_pf_name}'"
        the_str += f" ({self.f_let_type})"
        the_str += f", '{self.s_pf_name}'"
        the_str += f" ({self.s_let_type})"
        the_str += f": shift {self.shift:.4f}"
        the_str += f" [f_gly {len(self.f_gly_chop)}"
        the_str += f", s_gly {len(self.s_gly_chop)}"
        the_str += f", spline {len(self.spline_seq_con)}]"
        return the_str

    def __repr__(self):
        the_repr = self.__str__()
        the_repr += f"\nf_hash_sha1 {self.f_hash_sha1} s_hash_sha1 {self.s_hash_sha1}"
        the_repr += f"\nf_gly_chop {self.f_gly_chop} s_gly_chop {self.s_gly_chop}"
        the_repr += f"\nspline_seq_con {self.spline_seq_con}"
        return the_repr
