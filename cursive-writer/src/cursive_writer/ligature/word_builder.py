import argparse
import logging
import jsons  # type: ignore
import matplotlib.pyplot as plt  # type: ignore

from pathlib import Path
from copy import deepcopy

from typing import Dict, List
from cursive_writer.utils.type_utils import Glyph, ThickSpline

from cursive_writer.ligature.letter_class import Letter
from cursive_writer.ligature.ligature import align_letter_1
from cursive_writer.ligature.ligature import align_letter_2
from cursive_writer.ligature.ligature_info import LigatureInfo
from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils.geometric_utils import find_thick_spline_bbox
from cursive_writer.utils.geometric_utils import translate_spline_sequence
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

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env() -> argparse.Namespace:
    setup_logger()

    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 word_builder.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def load_letter_dict(data_dir: Path) -> Dict[str, Letter]:
    """TODO: what is load_letter_dict doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_letter_dict")
    logg.debug(f"Start load_letter_dict")

    letters_info: Dict[str, Letter] = {}
    letters_info["i"] = Letter(
        "i",
        left_type="low_up",
        right_type="low_up",
        # pf_spline_low=data_dir / "i2_l_000.txt",
        pf_spline_low=data_dir / "i2_l_dot_000.txt",
        # pf_spline_high=data_dir / "i1_h_006.txt",
        # pf_spline_high=data_dir / "i2_h_000.txt",
        pf_spline_high=data_dir / "i2_h_dot_000.txt",
    )
    letters_info["v"] = Letter(
        "v",
        left_type="high_down",
        right_type="high_up",
        # pf_spline_alone=data_dir / "v1_001.txt",
        pf_spline_alone=data_dir / "v2_002.txt",
    )
    letters_info["m"] = Letter(
        "m",
        left_type="high_down",
        right_type="low_up",
        pf_spline_alone=data_dir / "m2_000.txt",
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
        logg.debug(f"\nci_load: {ci_load!r}")
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
    logg.debug(f"\ncon_info: {con_info!r}")

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
) -> Dict[str, LigatureInfo]:
    """TODO: what is fill_ligature_info doing?
    """
    logg = logging.getLogger(f"c.{__name__}.fill_ligature_info")
    logg.debug(f"Start fill_ligature_info")

    # where to keep the connection info
    ligature_info: Dict[str, LigatureInfo] = {}

    for i in range(len(input_str) - 1):
        # get the current pair
        pair = input_str[i : i + 2]
        logg.debug(f"Doing pair: {pair}")

        # compute info for this pair if needed
        if pair not in ligature_info:
            f_let = letters_info[pair[0]]
            s_let = letters_info[pair[1]]
            ligature_info[pair] = compute_letter_alignement(
                f_let, s_let, x_stride, data_dir, ligature_dir
            )

    return ligature_info


def plot_results(all_glyphs_thick: ThickSpline) -> None:
    # find dimension of the plot
    xlim, ylim = find_thick_spline_bbox(all_glyphs_thick)
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
    for i_g, glyph in enumerate(all_glyphs_thick):
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

    letters_info = load_letter_dict(data_dir)
    logg.debug(f"letters_info:")
    for letter in letters_info:
        logg.debug(f"{letters_info[letter]}")

    # the sampling precision when shifting
    x_stride: float = 1

    # the thickness of the letters
    thickness: int = 10

    # the information on how to link the letter
    ligature_info = fill_ligature_info(
        args.input_str, letters_info, x_stride, data_dir, ligature_dir
    )

    # all the spline_seq points
    all_glyphs: List[Glyph] = []

    # the accumulated shift
    acc_shift: float = 0

    # draw the first letter
    all_glyphs.extend(letters_info[args.input_str[0]].get_spline_seq("alone"))

    for i in range(len(args.input_str) - 1):
        # get the current pair
        pair = args.input_str[i : i + 2]
        logg.debug(f"Doing pair: {pair}")

        # f_let = letters_info[pair[0]]
        s_let = letters_info[pair[1]]

        # edit the previous/first (if needed, some times it will be the same)
        # make a copy so that we do not modify the original
        f_gly_chop = deepcopy(ligature_info[pair].f_gly_chop)
        translate_spline_sequence([f_gly_chop], acc_shift, 0)
        all_glyphs[-1] = f_gly_chop

        # add the translated connection
        spline_seq_con = deepcopy(ligature_info[pair].spline_seq_con)
        translate_spline_sequence(spline_seq_con, acc_shift, 0)
        all_glyphs.extend(spline_seq_con)
        # logg.debug(f"spline_seq_con: {spline_seq_con}")

        # update the total shift
        acc_shift += ligature_info[pair].shift

        # add the second
        # translate the connection
        s_gly_chop = deepcopy(ligature_info[pair].s_gly_chop)
        translate_spline_sequence([s_gly_chop], acc_shift, 0)

        # extract the type of the second letter to use
        s_spline_seq = s_let.get_spline_seq(ligature_info[pair].s_let_type)
        # copy it to avoid modifying it
        # TODO add a flag in get_spline_seq to get a copy or the original
        s_spline_seq = deepcopy(s_spline_seq)
        # translate the spline
        translate_spline_sequence(s_spline_seq, acc_shift, 0)
        # change the first glyph of the spline
        s_spline_seq[0] = s_gly_chop
        # add the spline to the glyphs
        all_glyphs.extend(s_spline_seq)

    # compute the thick spline
    # TODO: only recompute the connecting glyphs, the rest of the letter is static
    all_glyphs_thick = compute_long_thick_spline(all_glyphs, thickness)

    # plot results
    plot_results(all_glyphs_thick)
    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_word_builder(args)
