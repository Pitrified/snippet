import argparse
import logging
import matplotlib.pyplot as plt
import numpy as np

from pathlib import Path
from random import seed as rseed
from timeit import default_timer as timer

from cursive_writer.utils.utils import load_spline
from cursive_writer.utils import plot_utils
from cursive_writer.spliner.spliner import compute_long_spline


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="h1_000.txt",
        help="path to input spline to use",
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


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    log_format_module = "%(name)s: %(message)s"
    #  log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    addLoggingLevel("TRACE", 5)


def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logging, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logging, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))
    if hasattr(logging.getLoggerClass(), methodName):
        raise AttributeError("{} already defined in logger class".format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            # Yes, logger takes its '*args' as 'args'
            self._log(levelNum, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)
    setattr(logging, methodName, logToRoot)


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
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()

    spline_samples = compute_long_spline(spline_sequence, thickness)

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
        "s1_000.txt",
        "t1_007.txt",
        "v1_001.txt",
        "z1_000.txt",
    ]

    for letter_name in good_letters:
        if not prefixes is None:
            if letter_name[0] in prefixes:
                pf_input_spline = data_dir / letter_name
                plot_letter(pf_input_spline, data_dir, thickness)


if __name__ == "__main__":
    args = setup_env()

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

    if args.which_plot == "single":
        plot_letter(pf_input_spline, data_dir, thickness)
    elif args.which_plot == "all":
        plot_good_letters(data_dir, thickness)
    else:
        # send the which_plot args as string of prefixes, only plot the letters sent
        plot_good_letters(data_dir, thickness, args.which_plot)

    # TODO a mode that monitors the files drawn and recomputes them

    plt.show()
