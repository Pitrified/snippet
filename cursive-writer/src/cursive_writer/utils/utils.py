import logging
import numpy as np

from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.oriented_point import OrientedPoint


def iterate_double_list(the_list):
    """Iterate over the elements of a list of lists

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for inner_list in the_list:
        for element in inner_list:
            yield element


def enumerate_double_list(the_list):
    """Enumerate the content of a list of lists, providing both indexes

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for i, inner_list in enumerate(the_list):
        for j, element in enumerate(inner_list):
            yield i, j, element


def find_free_index(folder, base_name_fmt):
    """Find the first free name
    """
    logg = logging.getLogger(f"c.{__name__}.find_free_index")
    logg.setLevel("TRACE")
    logg.info(f"Start {fmt_cn('find_free_index', 'a2')}")
    for i in range(1000):
        file_name = folder / base_name_fmt.format(i)
        if file_name.exists():
            logg.debug(f"Found file_name: {file_name}")
        else:
            logg.debug(f"Empty file_name: {file_name}")
            return i


def load_glyph(pf_input_glyph, dx, dy):
    """TODO: what is load_glyph doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_glyph")
    logg.debug(f"Start load_glyph")

    if not pf_input_glyph.exists():
        logg.warn(f"{pf_input_glyph} not found!")
        return None

    glyph = []

    with pf_input_glyph.open("r") as f:
        for line in f:
            # logg.debug(f"line: {line.rstrip()}")
            x, y, ori_deg = line.rstrip().split("\t")
            x = float(x)
            y = float(y)
            ori_deg = float(ori_deg)
            fm_pt = OrientedPoint(x + dx, y + dy, ori_deg)
            glyph.append(fm_pt)

    return glyph


def load_spline(pf_input_spline, data_dir):
    """TODO: what is load_spline doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_spline")
    logg.debug(f"Start load_spline")

    # full path to the letter recap file
    logg.debug(f"pf_input_spline: {pf_input_spline}")

    spline = []

    # open the spline file
    with pf_input_spline.open() as f:

        # in each line there is a glyph name, offset x y
        for line in f:
            logg.debug(f"line: {line.rstrip()}")
            glyph_name, dx, dy = line.rstrip().split("\t")
            dx = float(dx)
            dy = float(dy)
            current_glyph = data_dir / glyph_name
            logg.debug(f"current_glyph: {current_glyph}")

            glyph = load_glyph(current_glyph, dx, dy)

            # if the current_glyph file does not exist, skip it
            if glyph is None:
                continue

            spline.append(glyph)

    return spline


def print_coeff(coeff):
    """Prints coeff as equation
    """
    # logg = logging.getLogger(f"c.{__name__}.print_coeff")
    # logg.debug(f"Start print_coeff {coeff}")

    eq_str = "y ="
    for i, c in enumerate(np.flip(coeff)):
        eq_str += f" + {c} * x^{i}"

    return eq_str
