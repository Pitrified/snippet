import argparse
import logging
import matplotlib.pyplot as plt

from pathlib import Path

from cursive_writer.utils.utils import load_spline
from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils.setup import setup_logger


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="h1_000.txt",
        help="Path to input spline to use",
    )

    parser.add_argument(
        "-t",
        "--thickness",
        type=int,
        default=10,
        help="Thickness of the generated spline",
    )

    parser.add_argument(
        "-wp",
        "--which_plot",
        type=str,
        default="single",
        help="Which letter to plot, choose 'single', 'all' of a string of letters to show",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env():
    setup_logger()

    args = parse_arguments()

    recap = f"python3 single_spline2image.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def plot_letter(pf_input_spline, data_dir, thickness):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.plot_letter")
    logg.debug(f"Starting plot_letter")

    spline_sequence = load_spline(pf_input_spline, data_dir)
    # logg.debug(f"spline_sequence: {spline_sequence}")

    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")
    for glyph in spline_sequence:
        for point in glyph:
            # logg.debug(f"point: {point}")
            if point.x > max_x:
                max_x = point.x
            if point.x < min_x:
                min_x = point.x
            if point.y > max_y:
                max_y = point.y
            if point.y < min_y:
                min_y = point.y
    logg.debug(f"max_x: {max_x} min_x: {min_x} max_y: {max_y} min_y: {min_y}")
    wid = max_x - min_x
    hei = max_y - min_y

    # inches to point
    ratio = 4 / 1000

    fig_dims = (wid * ratio, hei * ratio)

    # fig, ax = plt.subplots(figsize=fig_dims)
    # fig, ax = plt.subplots()

    fig = plt.figure(figsize=fig_dims, frameon=False)
    fig.canvas.set_window_title(f"{pf_input_spline.stem}")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()

    spline_samples = compute_long_thick_spline(spline_sequence, thickness)

    for glyph in spline_samples:
        for segment in glyph:
            ax.plot(*segment, color="k", marker=".", ls="")

    # plt.yticks(rotation=90)

    # plot everything
    # plot_utils.plot_build(fig, ax)
    # fig.tight_layout()
    # ax.set_yticklabels(ax.get_yticklabels(), rotation=90)


def plot_good_letters(data_dir, thickness, prefixes=None):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.plot_good_letters")
    logg.debug(f"Starting plot_good_letters")

    good_letters = [
        "f1_002.txt",
        "h1_002.txt",
        "i1_006.txt",
        "i1_h_006.txt",
        "m1_001.txt",
        "n1_000.txt",
        "s1_000.txt",
        "t1_007.txt",
        "v1_001.txt",
        "z1_000.txt",
    ]

    for letter_name in good_letters:
        if prefixes is None or letter_name[0] in prefixes:
            pf_input_spline = data_dir / letter_name
            plot_letter(pf_input_spline, data_dir, thickness)


def run_single_spline2image(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_single_spline2image")
    logg.debug(f"Starting run_single_spline2image")

    plt.rcParams["toolbar"] = "None"

    logg = logging.getLogger(f"c.{__name__}.main")
    logg.debug(f"Starting main")

    main_dir = Path(__file__).resolve().parent
    logg.debug(f"main_dir: {main_dir}")
    data_dir = main_dir / "data"
    logg.debug(f"data_dir: {data_dir}")

    path_input = args.path_input
    pf_input_spline = data_dir / path_input
    logg.debug(f"pf_input_spline: {pf_input_spline}")

    thickness = args.thickness

    logg.debug(f"args.which_plot: {args.which_plot}")

    if args.which_plot == "single":
        plot_letter(pf_input_spline, data_dir, thickness)
    elif args.which_plot == "all":
        plot_good_letters(data_dir, thickness)
    else:
        # send the which_plot args as string of prefixes, only plot the letters sent
        plot_good_letters(data_dir, thickness, args.which_plot)

    # TODO a mode that monitors the files drawn and recomputes them

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_single_spline2image(args)
