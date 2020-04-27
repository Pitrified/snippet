import logging
import json
import numpy as np  # type: ignore

from hashlib import sha1
from pathlib import Path

from typing import Iterable, Iterator, Optional, Tuple, TypeVar
from cursive_writer.utils.type_utils import DArray, Glyph, Spline

from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.oriented_point import OrientedPoint

T = TypeVar("T")


def iterate_double_list(the_list: Iterable[Iterable[T]]) -> Iterator[T]:
    """Iterate over the elements of a list of lists

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for inner_list in the_list:
        for element in inner_list:
            yield element


def enumerate_double_list(
    the_list: Iterable[Iterable[T]],
) -> Iterator[Tuple[int, int, T]]:
    """Enumerate the content of a list of lists, providing both indexes

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for i, inner_list in enumerate(the_list):
        for j, element in enumerate(inner_list):
            yield i, j, element


def find_free_index(folder: Path, base_name_fmt: str) -> Optional[int]:
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

    return None


def load_glyph(pf_input_glyph: Path, dx: float = 0, dy: float = 0) -> Optional[Glyph]:
    """TODO: what is load_glyph doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_glyph")
    logg.setLevel("INFO")
    logg.debug(f"Start load_glyph")

    if not pf_input_glyph.exists():
        logg.warn(f"{pf_input_glyph} not found!")
        return None

    glyph = []

    with pf_input_glyph.open("r") as f:
        for line in f:
            logg.debug(f"line: {line.rstrip()}")
            # x, y, ori_deg = line.rstrip().split("\t")
            # x = float(x)
            # y = float(y)
            # ori_deg = float(ori_deg)
            pz = line.rstrip().split("\t")
            x, y, ori_deg = map(float, pz)
            fm_pt = OrientedPoint(x + dx, y + dy, ori_deg)
            glyph.append(fm_pt)

    return glyph


def load_spline(
    pf_input_spline: Path, data_dir: Path, dx: float = 0, dy: float = 0
) -> Spline:
    """TODO: what is load_spline doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_spline")
    logg.setLevel("INFO")
    logg.debug(f"Start load_spline")

    # full path to the letter recap file
    logg.debug(f"pf_input_spline: {pf_input_spline}")

    spline = []

    # open the spline file
    with pf_input_spline.open() as f:

        # in each line there is a glyph name, offset x y
        for line in f:
            logg.debug(f"line: {line.rstrip()}")
            glyph_name, s_dx, s_dy = line.rstrip().split("\t")
            dx = float(s_dx)
            dy = float(s_dy)
            current_glyph = data_dir / glyph_name
            logg.debug(f"current_glyph: {current_glyph}")

            glyph = load_glyph(current_glyph, dx, dy)

            # if the current_glyph file does not exist, skip it
            if glyph is None:
                continue

            spline.append(glyph)

    return spline


def compute_hash_spline(pf_spline: Path, data_dir: Path) -> str:
    """TODO: what is compute_hash_spline doing?
    """
    logg = logging.getLogger(f"c.{__name__}.compute_hash_spline")
    logg.debug(f"Start compute_hash_spline")

    hash_sha1 = sha1()
    hash_sha1.update(pf_spline.read_bytes())

    with pf_spline.open() as fs:
        # in each line there is a glyph name, offset x y
        for line in fs:
            glyph_name, _, _ = line.rstrip().split("\t")
            current_glyph = data_dir / glyph_name
            hash_sha1.update(current_glyph.read_bytes())

    return hash_sha1.hexdigest()


def print_coeff(coeff: DArray) -> str:
    """Prints coeff as equation
    """
    # logg = logging.getLogger(f"c.{__name__}.print_coeff")
    # logg.debug(f"Start print_coeff {coeff}")

    eq_str = "y ="
    for i, c in enumerate(np.flip(coeff)):
        eq_str += f" + {c} * x^{i}"

    return eq_str


class OrientedPointEncoder(json.JSONEncoder):
    """Encoder for an OrientedPoint
    """

    def default(self, obj):
        """TODO: what is default doing?
        """
        if isinstance(obj, OrientedPoint):
            return {
                "_type": "OrientedPoint",
                "x": obj.x,
                "y": obj.y,
                "ori_deg": obj.ori_deg,
            }
        return super().default(obj)


class OrientedPointDecoder(json.JSONDecoder):
    """Decoder for OrientedPoint
    """

    def __init__(self, *args, **kwargs):
        """TODO: what is __init__ doing?
        """
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        """TODO: what is object_hook doing?
        """
        if "_type" not in obj:
            return obj
        if obj["_type"] == "OrientedPoint":
            x = obj["x"]
            y = obj["y"]
            ori_deg = obj["ori_deg"]
            return OrientedPoint(x, y, ori_deg)
        return obj


def serializer_oriented_point(obj: OrientedPoint, **kwargs):
    """
    """
    return {"x": obj.x, "y": obj.y, "ori_deg": obj.ori_deg}
