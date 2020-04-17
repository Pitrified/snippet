import argparse
import logging
import matplotlib.pyplot as plt

from pathlib import Path

from cursive_writer.spliner.spliner import compute_long_thick_spline
from cursive_writer.utils.geometric_utils import find_spline_sequence_bbox
from cursive_writer.utils.setup import setup_logger
from cursive_writer.utils.utils import load_spline


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

    parser.add_argument(
        "-col",
        "--colors",
        type=str,
        default="k",
        help="Color to use, set 'cycle' to use a different one in each glyph",
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


def plot_letter(pf_input_spline, data_dir, thickness, color="k"):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.plot_letter")
    logg.debug(f"Starting plot_letter")

    spline_sequence = load_spline(pf_input_spline, data_dir)
    # logg.debug(f"spline_sequence: {spline_sequence}")

    # inches to point
    ratio = 4 / 1000
    # find plot dimension
    xlim, ylim = find_spline_sequence_bbox(spline_sequence)
    wid = xlim[1] - xlim[0]
    hei = ylim[1] - ylim[0]
    fig_dims = (wid * ratio, hei * ratio)

    fig = plt.figure(figsize=fig_dims, frameon=False)
    fig.canvas.set_window_title(f"{pf_input_spline.stem}")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()

    spline_samples = compute_long_thick_spline(spline_sequence, thickness)

    colors = ["b", "g", "r", "c", "m", "y", "k"]

    i = 0

    for glyph in spline_samples:
        for segment in glyph:
            if color == "cycle":
                mod = i % len(colors)
                ax.plot(*segment, color=colors[mod], marker=".", ls="")
            elif color in colors:
                ax.plot(*segment, color=color, marker=".", ls="")
            else:
                ax.plot(*segment, color="k", marker=".", ls="")
        i += 1


def plot_good_letters(data_dir, thickness, colors, prefixes=None):
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
            plot_letter(pf_input_spline, data_dir, thickness, colors)


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
        plot_letter(pf_input_spline, data_dir, thickness, args.colors)
    elif args.which_plot == "all":
        plot_good_letters(data_dir, thickness, args.colors)
    else:
        # send the which_plot args as string of prefixes, only plot the letters sent
        plot_good_letters(data_dir, thickness, args.colors, args.which_plot)

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_single_spline2image(args)
