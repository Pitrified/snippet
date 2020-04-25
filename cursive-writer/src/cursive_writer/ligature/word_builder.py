import argparse
import logging

from pathlib import Path

from cursive_writer.utils.setup import setup_logger
from cursive_writer.ligature.letter_class import Letter
from cursive_writer.ligature.ligature import align_letter_2
from cursive_writer.utils.utils import load_spline


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="hp.jpg",
        help="path to input image to use",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env():
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


def load_letter_dict(data_dir):
    """TODO: what is load_letter_dict doing?
    """
    logg = logging.getLogger(f"c.{__name__}.load_letter_dict")
    logg.debug(f"Start load_letter_dict")

    letters_info = {}
    letters_info["i"] = Letter(
        "i",
        left_type="low_up",
        right_type="low_up",
        pf_spline_low=data_dir / "i2_l_000.txt",
        pf_spline_high=data_dir / "i1_h_006.txt",
    )
    letters_info["v"] = Letter(
        "v",
        left_type="high_down",
        right_type="high_up",
        pf_spline_alone=data_dir / "v1_001.txt",
    )
    letters_info["m"] = Letter(
        "m",
        left_type="high_down",
        right_type="low_up",
        pf_spline_alone=data_dir / "m2_000.txt",
    )
    return letters_info


def compute_letter_alignement(f_let, s_let, x_stride, data_dir):
    """TODO: what is compute_letter_alignement doing?
    """
    logg = logging.getLogger(f"c.{__name__}.compute_letter_alignement")
    logg.debug(f"Start compute_letter_alignement {f_let} {s_let}")

    # pick the correct align strategy

    # something like im or iv
    if f_let.right_type == "low_up" and s_let.left_type == "high_down":

        # the right side at the moment does not change, so get any one
        pf_spline_left = f_let.get_pf("alone")

        # we request the high because this *is* a high letter
        pf_spline_right = s_let.get_pf("high")

        # load and compute
        spline_seq_l = load_spline(pf_spline_left, data_dir)
        spline_seq_r = load_spline(pf_spline_right, data_dir)
        spline_seq_con, shift, _ = align_letter_2(spline_seq_l, spline_seq_r, x_stride)

        # there is no need to chop the last/first glyphs
        gly_chop_l = spline_seq_l[-1]
        gly_chop_r = spline_seq_r[0]

    # all other cases use align_letter_1
    else:

        # need to pick the correct version of the letters to join

        # the right side at the moment does not change, so get any one
        pf_spline_left = f_let.get_pf("alone")
        # look at the right of the first letter
        if f_let.right_type == "high_up":
            # use high version of the second letter
            pf_spline_right = s_let.get_pf("high")
        elif f_let.right_type == "low_up":
            # use low version of the second letter
            pf_spline_right = s_let.get_pf("low")

        # load and compute
        spline_seq_l = load_spline(pf_spline_left, data_dir)
        spline_seq_r = load_spline(pf_spline_right, data_dir)
        spline_seq_con, gly_chop_l, gly_chop_r, shift, = align_letter_2(
            spline_seq_l, spline_seq_r, x_stride
        )

    return spline_seq_con, gly_chop_l, gly_chop_r, shift


def run_word_builder(args):
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

    ligature_info = {}

    x_stride = 1

    pair = "ii"

    if pair not in ligature_info:
        f_let = letters_info[pair[0]]
        s_let = letters_info[pair[1]]
        ligature_info[pair] = compute_letter_alignement(
            f_let, s_let, x_stride, data_dir
        )


if __name__ == "__main__":
    args = setup_env()
    run_word_builder(args)
