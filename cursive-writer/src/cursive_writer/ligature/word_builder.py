import argparse
import logging
import jsons  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from pathlib import Path
from copy import deepcopy

from typing import Dict, Tuple
from cursive_writer.utils.type_utils import ThickSpline

from cursive_writer.utils.geometric_utils import translate_spline_sequence
from cursive_writer.ligature.letter_class import Letter
from cursive_writer.ligature.ligature import align_letter_1
from cursive_writer.ligature.ligature import align_letter_2
from cursive_writer.ligature.ligature_info import LigatureInfo
from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils.geometric_utils import find_thick_spline_bbox
from cursive_writer.utils.geometric_utils import translate_thick_spline
from cursive_writer.utils.oriented_point import OrientedPoint
from cursive_writer.utils.setup import setup_logger
from cursive_writer.utils.utils import serializer_oriented_point


def parse_arguments() -> argparse.Namespace:
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--input_str",
        type=str,
        default="vivvmmiimv",
        help="Input string to write",
    )

    parser.add_argument(
        "-t", "--thickness", type=int, default=10, help="Thickness of the pen"
    )

    parser.add_argument(
        "-llt",
        "--log_level_type",
        type=str,
        default="m",
        help="Message format for the debugging logger",
        choices=["anlm", "nlm", "lm", "nm", "m"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env() -> argparse.Namespace:
    args = parse_arguments()

    setup_logger("DEBUG", args.log_level_type)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 word_builder.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def load_letter_dict(thickness: int, data_dir: Path) -> Dict[str, Letter]:
    """TODO: what is load_letter_dict doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_letter_dict")
    logg.debug(f"Start load_letter_dict")

    letters_info: Dict[str, Letter] = {}
    letters_info["i"] = Letter(
        "i",
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / "i2_l_dot_000.txt",
        pf_spline_high=data_dir / "i2_h_dot_000.txt",
        thickness=thickness,
    )
    letters_info["v"] = Letter(
        "v",
        left_type="high_down",
        right_type="high_up",
        pf_spline_alone=data_dir / "v2_002.txt",
        thickness=thickness,
    )
    letters_info["m"] = Letter(
        "m",
        left_type="high_down",
        right_type="low_up",
        pf_spline_alone=data_dir / "m2_000.txt",
        thickness=thickness,
    )
    letters_info["n"] = Letter(
        "n",
        left_type="high_down",
        right_type="low_up",
        pf_spline_alone=data_dir / "n2_000.txt",
        thickness=thickness,
    )
    letters_info["u"] = Letter(
        "u",
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / "u2_l_000.txt",
        pf_spline_high=data_dir / "u2_h_000.txt",
        thickness=thickness,
    )
    letters_info["v"] = Letter(
        "v",
        left_type="high_down",
        right_type="high_up",
        pf_spline_alone=data_dir / "v2_002.txt",
        thickness=thickness,
    )
    return letters_info


def compute_letter_alignement(
    f_let: Letter, s_let: Letter, x_stride: float, data_dir: Path, ligature_dir: Path
) -> LigatureInfo:
    """TODO: what is compute_letter_alignement doing?
    """
    logg = logging.getLogger(f"c.{__name__}.compute_letter_alignement")
    logg.debug(f"Start compute_letter_alignement {f_let.letter} {s_let.letter}")

    # pick the correct align strategy

    # something like im or iv
    if f_let.right_type == "low_up" and s_let.left_type == "high_down":
        strategy = "align_letter_2"

        # the right side at the moment does not change, so get any one
        f_let_type = "alone"
        f_spline_seq = f_let.get_spline_seq(f_let_type)
        f_pf_name = f_let.get_pf(f_let_type).name
        f_hash_sha1 = f_let.get_hash(f_let_type)

        # we request the high because this *is* a high letter
        s_let_type = "high"
        s_spline_seq = s_let.get_spline_seq(s_let_type)
        s_pf_name = s_let.get_pf(s_let_type).name
        s_hash_sha1 = s_let.get_hash(s_let_type)

    # all other cases use align_letter_1
    else:
        strategy = "align_letter_1"

        # need to pick the correct version of the letters to join

        # the right side at the moment does not change, so get any one
        f_let_type = "alone"
        f_spline_seq = f_let.get_spline_seq(f_let_type)
        f_pf_name = f_let.get_pf(f_let_type).name
        f_hash_sha1 = f_let.get_hash(f_let_type)

        # look at the right of the first letter
        if f_let.right_type == "high_up":
            # use high version of the second letter
            s_let_type = "high"
        elif f_let.right_type == "low_up":
            # use low version of the second letter
            s_let_type = "low"

        # get relevant informations
        s_spline_seq = s_let.get_spline_seq(s_let_type)
        s_pf_name = s_let.get_pf(s_let_type).name
        s_hash_sha1 = s_let.get_hash(s_let_type)

    # load, if available, the ligature for this
    ligature_pf = ligature_dir / f"{f_let.letter}{s_let.letter}.txt"
    if ligature_pf.exists():
        # load the saved LigatureInfo
        ci_load = jsons.loads(ligature_pf.read_text(), LigatureInfo)

        # decide if the ligature loaded is the same
        # logg.debug(f"ci_load: {ci_load!r}")
        logg.debug(f"ci_load: {ci_load}")
        if f_pf_name != ci_load.f_pf_name or s_pf_name != ci_load.s_pf_name:
            logg.debug(f"The names in the loaded info are different than the current")
            equals = False
        elif f_let_type != ci_load.f_let_type or s_let_type != ci_load.s_let_type:
            logg.debug(f"The letter types in the loaded info are different")
            equals = False
        elif f_hash_sha1 != ci_load.f_hash_sha1 or s_hash_sha1 != ci_load.s_hash_sha1:
            logg.debug(f"The hash_sha1 in the loaded info are different")
            equals = False
        else:
            logg.debug(f"The ligature is valid!")
            equals = True

        if equals:
            return ci_load

    if strategy == "align_letter_2":
        # load and compute
        spline_seq_con, shift, _ = align_letter_2(f_spline_seq, s_spline_seq, x_stride)

        # there is no need to chop the last/first glyphs
        f_gly_chop = f_spline_seq[-1]
        s_gly_chop = s_spline_seq[0]

    else:
        # load and compute
        spline_seq_con, f_gly_chop, s_gly_chop, shift, = align_letter_1(
            f_spline_seq, s_spline_seq, x_stride
        )

    con_info = LigatureInfo(
        f_pf_name=f_pf_name,
        s_pf_name=s_pf_name,
        f_let_type=f_let_type,
        s_let_type=s_let_type,
        spline_seq_con=spline_seq_con,
        f_gly_chop=f_gly_chop,
        s_gly_chop=s_gly_chop,
        shift=shift,
        f_hash_sha1=f_hash_sha1,
        s_hash_sha1=s_hash_sha1,
    )
    # logg.debug(f"con_info: {con_info!r}")
    logg.debug(f"con_info: {con_info}")

    # save the LigatureInfo
    jsons.set_serializer(serializer_oriented_point, OrientedPoint)
    ligature_info_encoded = jsons.dumps(con_info, indent=4)
    logg.debug(f"\nligature_info_encoded: {ligature_info_encoded}")

    with ligature_pf.open("w") as f_li:
        f_li.write(ligature_info_encoded)

    return con_info


def fill_ligature_info(
    input_str: str,
    letters_info: Dict[str, Letter],
    x_stride: float,
    data_dir: Path,
    ligature_dir: Path,
    thickness: int,
) -> Tuple[Dict[str, LigatureInfo], Dict[str, ThickSpline]]:
    """TODO: what is fill_ligature_info doing?
    """
    logg = logging.getLogger(f"c.{__name__}.fill_ligature_info")
    logg.debug(f"Start fill_ligature_info")

    # where to keep the connection info
    ligature_info: Dict[str, LigatureInfo] = {}
    thick_con_info: Dict[str, ThickSpline] = {}

    for i in range(len(input_str) - 1):
        # get the current pair
        pair = input_str[i : i + 2]
        logg.debug(f"\nDoing pair: {pair}")

        # compute info for this pair if needed
        if pair not in ligature_info:
            f_let = letters_info[pair[0]]
            s_let = letters_info[pair[1]]
            ligature_info[pair] = compute_letter_alignement(
                f_let, s_let, x_stride, data_dir, ligature_dir
            )
        else:
            logg.debug(f"Pair already computed")

        # link all the spline info
        full_spline_con = [ligature_info[pair].f_gly_chop]
        full_spline_con.extend(ligature_info[pair].spline_seq_con)
        # shift the second glyph
        s_gly_chop = deepcopy(ligature_info[pair].s_gly_chop)
        shift = ligature_info[pair].shift
        translate_spline_sequence([s_gly_chop], shift, 0)
        full_spline_con.append(s_gly_chop)

        # precompute the full thick ligature information
        full_thick_con = compute_long_thick_spline(full_spline_con, thickness)
        thick_con_info[pair] = full_thick_con

    return ligature_info, thick_con_info


def build_word(
    input_str: str,
    letters_info: Dict[str, Letter],
    ligature_info: Dict[str, LigatureInfo],
    thick_con_info: Dict[str, ThickSpline],
) -> ThickSpline:
    """TODO: what is build_word doing?
    """
    logg = logging.getLogger(f"c.{__name__}.build_word")
    logg.debug(f"Start build_word")

    # the final thick spline for the word
    word_thick_spline: ThickSpline = []

    # the accumulated shift
    acc_shift: float = 0

    # the first letter of the word
    first_letter = args.input_str[0]

    # save the first thick letter
    word_thick_spline.extend(letters_info[first_letter].get_thick_samples("alone"))

    for i in range(len(args.input_str) - 1):
        # get the current pair
        pair = args.input_str[i : i + 2]
        logg.debug(f"Doing pair: {pair}")

        # extract the second letter info
        s_let = letters_info[pair[1]]

        # remove the last glyph: it will be replaecd by the first of the thick_spline_con
        word_thick_spline.pop()

        # extract the thick connection
        thick_spline_con = thick_con_info[pair]
        # translate it
        tra_thick_spline_con = translate_thick_spline(thick_spline_con, acc_shift, 0)
        word_thick_spline.extend(tra_thick_spline_con)

        # update the total shift
        acc_shift += ligature_info[pair].shift

        # add the second letter
        # extract the thick spline of the correct type of the second letter to use
        s_thick_spline = s_let.get_thick_samples(ligature_info[pair].s_let_type)
        # translate it
        s_tra_thick_spline = translate_thick_spline(s_thick_spline, acc_shift, 0)
        # add it to the list of glyphs, without the first glyph
        word_thick_spline.extend(s_tra_thick_spline[1:])

    return word_thick_spline


def plot_results(thick_spline: ThickSpline) -> None:
    # find dimension of the plot
    xlim, ylim = find_thick_spline_bbox(thick_spline)
    # inches to point
    ratio = 3 / 1000
    wid = xlim[1] - xlim[0]
    hei = ylim[1] - ylim[0]
    fig_dims = (wid * ratio, hei * ratio)
    # create plot
    fig = plt.figure(figsize=fig_dims, frameon=False)
    ax = fig.add_axes((0, 0, 1, 1))
    fig.canvas.set_window_title(f"Writing {args.input_str}")
    ax.set_axis_off()

    # style = {"color": "k", "marker": ".", "ls": ""}
    # col_list = ["g", "r", "y", "c", "m", "k", "b"]
    col_list = ["k"]
    # i_s = 0
    for i_g, glyph in enumerate(thick_spline):
        # logg.debug(f"Plotting glyph: {glyph}")
        cc = col_list[i_g % len(col_list)]
        style = {"color": cc, "marker": ".", "ls": ""}
        for segment in glyph:
            # cc = col_list[i_s % len(col_list)]
            # i_s += 1
            # style = {"color": cc, "marker": ".", "ls": ""}
            ax.plot(*segment, **style)


def run_word_builder(args: argparse.Namespace) -> None:
    """TODO: What is word_builder doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_word_builder")
    logg.debug(f"Starting run_word_builder")

    main_dir = Path(__file__).resolve().parent
    logg.debug(f"main_dir: {main_dir}")
    data_dir = main_dir.parent / "data"
    logg.debug(f"data_dir: {data_dir}")
    ligature_dir = main_dir.parent / "connections"
    logg.debug(f"ligature_dir {ligature_dir}")
    if not ligature_dir.exists():
        ligature_dir.mkdir(parents=True)

    thickness = args.thickness if args.thickness > 0 else 1

    letters_info = load_letter_dict(thickness, data_dir)
    logg.debug(f"letters_info:")
    for letter in letters_info:
        logg.debug(f"{letters_info[letter]}")

    # the sampling precision when shifting
    x_stride: float = 1

    # the information on how to link the letters
    ligature_info, thick_con_info = fill_ligature_info(
        args.input_str, letters_info, x_stride, data_dir, ligature_dir, thickness
    )

    word_thick_spline = build_word(
        args.input_str, letters_info, ligature_info, thick_con_info
    )

    # plot results
    plot_results(word_thick_spline)
    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_word_builder(args)
