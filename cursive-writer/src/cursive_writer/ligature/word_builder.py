import argparse
import logging

from pathlib import Path

from cursive_writer.utils.setup import setup_logger
from cursive_writer.ligature.letter_class import Letter


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
        "i", "low_up", "low_up", data_dir / "i2_l_000.txt", data_dir / "i1_h_006.txt"
    )
    letters_info["v"] = Letter("v", "high_down", "high_up", data_dir / "v1_001.txt")
    letters_info["m"] = Letter("m", "high_down", "low_up", data_dir / "m2_000.txt")
    return letters_info


def compute_letter_alignement(pair, letters_info):
    """TODO: what is compute_letter_alignement doing?
    """
    logg = logging.getLogger(f"c.{__name__}.compute_letter_alignement")
    l_let = pair[0]
    r_let = pair[1]
    logg.debug(f"Start compute_letter_alignement {l_let} {r_let}")


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

    pair = "ii"

    if pair not in ligature_info:
        ligature_info[pair] = compute_letter_alignement(pair, letters_info)


if __name__ == "__main__":
    args = setup_env()
    run_word_builder(args)
