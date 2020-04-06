import logging

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


def load_spline(pf_input_spline, data_dir):
    """TODO: what is load_spline doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_spline")
    logg.debug(f"Start load_spline")

    # full path to the letter recap file
    logg.debug(f"pf_input_spline: {pf_input_spline}")

    # letter name
    spline_name_stem = pf_input_spline.stem
    # template for the glyph files
    glyph_name_fmt = f"{spline_name_stem}_{{:03d}}.txt"
    logg.debug(f"data_dir {data_dir} glyph_name_fmt {glyph_name_fmt}")

    spline = []

    for i in range(1000):
        current_glyph = data_dir / glyph_name_fmt.format(i)
        logg.debug(f"current_glyph: {current_glyph}")

        if not current_glyph.exists():
            logg.debug(f"No more glyphs")
            break

        glyph = []
        with current_glyph.open("r") as f:
            for line in f:
                # logg.debug(f"line: {line.rstrip()}")
                x, y, ori_deg = line.rstrip().split("\t")
                x = float(x)
                y = float(y)
                ori_deg = float(ori_deg)
                fm_pt = OrientedPoint(x, y, ori_deg)
                glyph.append(fm_pt)

        spline.append(glyph)

    return spline
