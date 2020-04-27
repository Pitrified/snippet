import argparse
import logging
import matplotlib.pyplot as plt  # type: ignore

from pathlib import Path
from copy import deepcopy

from typing import Dict

from cursive_writer.ligature.letter_class import Letter
from cursive_writer.ligature.ligature import align_letter_1
from cursive_writer.ligature.ligature import align_letter_2
from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils.geometric_utils import find_spline_sequence_bbox
from cursive_writer.utils.geometric_utils import translate_spline_sequence
from cursive_writer.utils.setup import setup_logger


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
    f_let: Letter, s_let: Letter, x_stride: float, data_dir: Path
):
    """TODO: what is compute_letter_alignement doing?
    """
    logg = logging.getLogger(f"c.{__name__}.compute_letter_alignement")
    logg.debug(f"Start compute_letter_alignement {f_let.letter} {s_let.letter}")

    # pick the correct align strategy

    # something like im or iv
    if f_let.right_type == "low_up" and s_let.left_type == "high_down":

        # the right side at the moment does not change, so get any one
        spline_seq_l = f_let.get_spline_seq("alone")

        # we request the high because this *is* a high letter
        spline_seq_r = s_let.get_spline_seq("high")

        # load and compute
        spline_seq_con, shift, _ = align_letter_2(spline_seq_l, spline_seq_r, x_stride)

        # there is no need to chop the last/first glyphs
        gly_chop_l = spline_seq_l[-1]
        gly_chop_r = spline_seq_r[0]

    # all other cases use align_letter_1
    else:

        # need to pick the correct version of the letters to join

        # the right side at the moment does not change, so get any one
        spline_seq_l = f_let.get_spline_seq("alone")

        # look at the right of the first letter
        if f_let.right_type == "high_up":
            # use high version of the second letter
            spline_seq_r = s_let.get_spline_seq("high")
        elif f_let.right_type == "low_up":
            # use low version of the second letter
            spline_seq_r = s_let.get_spline_seq("low")

        # load and compute
        spline_seq_con, gly_chop_l, gly_chop_r, shift, = align_letter_1(
            spline_seq_l, spline_seq_r, x_stride
        )

    # TODO turn this into a class
    con_info = {}
    con_info["spline_seq_con"] = spline_seq_con
    con_info["spline_seq_l"] = spline_seq_l
    con_info["spline_seq_r"] = spline_seq_r
    con_info["gly_chop_l"] = gly_chop_l
    con_info["gly_chop_r"] = gly_chop_r
    con_info["shift"] = shift
    # logg.debug(f"con_info: {con_info}")
    return con_info


def run_word_builder(args: argparse.Namespace) -> None:
    """TODO: What is word_builder doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_word_builder")
    logg.debug(f"Starting run_word_builder")

    main_dir = Path(__file__).resolve().parent
    logg.debug(f"main_dir: {main_dir}")
    data_dir = main_dir.parent / "data"
    logg.debug(f"data_dir: {data_dir}")

    letters_info = load_letter_dict(data_dir)
    logg.debug(f"letters_info:")
    for letter in letters_info:
        logg.debug(f"{letters_info[letter]}")

    # where to keep the connection info
    ligature_info = {}

    # the sampling precision when shifting
    x_stride = 1

    thickness = 10

    # all the spline_seq points
    all_glyphs = []

    # the accumulated shift
    acc_shift = 0

    # draw the first letter
    all_glyphs.extend(letters_info[args.input_str[0]].get_spline_seq("alone"))

    for i in range(len(args.input_str) - 1):
        # get the current pair
        pair = args.input_str[i : i + 2]
        logg.debug(f"Doing pair: {pair}")

        # compute info for this pair if needed
        if pair not in ligature_info:
            f_let = letters_info[pair[0]]
            s_let = letters_info[pair[1]]
            ligature_info[pair] = compute_letter_alignement(
                f_let, s_let, x_stride, data_dir
            )

        # edit the previous/first (if needed, some times it will be the same)
        # make a copy so that we do not modify the original
        gly_chop_l = deepcopy(ligature_info[pair]["gly_chop_l"])
        translate_spline_sequence([gly_chop_l], acc_shift, 0)
        all_glyphs[-1] = gly_chop_l

        # add the translated connection
        spline_seq_con = deepcopy(ligature_info[pair]["spline_seq_con"])
        translate_spline_sequence(spline_seq_con, acc_shift, 0)
        all_glyphs.extend(spline_seq_con)
        logg.debug(f"spline_seq_con: {spline_seq_con}")

        # update the total shift
        acc_shift += ligature_info[pair]["shift"]

        # add the second
        # translate the connection
        gly_chop_r = deepcopy(ligature_info[pair]["gly_chop_r"])
        translate_spline_sequence([gly_chop_r], acc_shift, 0)
        # translate the spline
        spline_seq_r = deepcopy(ligature_info[pair]["spline_seq_r"])
        translate_spline_sequence(spline_seq_r, acc_shift, 0)
        # change the first glyph of the spline
        spline_seq_r[0] = gly_chop_r
        # add the spline to the glyphs
        all_glyphs.extend(spline_seq_r)

    # plot results

    # find dimension of the plot
    xlim, ylim = find_spline_sequence_bbox(all_glyphs)
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

    # compute the thick spline

    all_glyphs_thick = compute_long_thick_spline(all_glyphs, thickness)
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

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_word_builder(args)
