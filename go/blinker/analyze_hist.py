"""Analyze the blink history."""
import argparse
import logging
import matplotlib.pyplot as plt  # type: ignore
import numpy as np  # type: ignore
from pathlib import Path
import typing as ty


# from timeit import default_timer as timer


def parse_arguments() -> argparse.Namespace:
    r"""Setup CLI interface.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="")

    default = "WARN"
    parser.add_argument(
        "--console_log_level",
        type=str,
        default=default,
        help=f"Level for the console logger, default {default}",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    default = "lnm"
    parser.add_argument(
        "--console_fmt_type",
        type=str,
        default=default,
        help=f"Message format for the console logger, default {default}",
        choices=["lanm", "lnm", "lm", "nm", "m"],
    )

    def_int = 500
    parser.add_argument(
        "-n",
        "--fireflies_num",
        type=int,
        default=default,
        help=f"Number of fireflies in the swarm, default {def_int}",
    )

    def_int = 10
    parser.add_argument(
        "-c",
        "--fireflies_comm",
        type=int,
        default=default,
        help=f"Number of fireflies to communicate with, default {def_int}",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(
    console_fmt_type: str = "m",
    console_log_level: str = "WARN",
    ui_fmt_type: ty.Optional[str] = None,
    ui_log_level: str = "INFO",
    file_fmt_type: ty.Optional[str] = None,
    file_log_level: str = "WARN",
    file_log_path: ty.Optional[Path] = None,
    file_log_mode: str = "a",
) -> None:
    r"""Setup loggers for the module.

    Args:
        console_fmt_type: Message format for the console logger.
        console_log_level: Logger level for the console logger.
    """
    # setup the format strings
    format_types = {}
    format_types["lanm"] = "[%(levelname)-8s] %(asctime)s %(name)s: %(message)s"
    format_types["lnm"] = "[%(levelname)-8s] %(name)s: %(message)s"
    format_types["lm"] = "[%(levelname)-8s]: %(message)s"
    format_types["nm"] = "%(name)s: %(message)s"
    format_types["m"] = "%(message)s"

    # setup the console handler with the console formatter
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(format_types[console_fmt_type])
    console_handler.setFormatter(console_formatter)

    # setup the console logger with the console handler
    logconsole = logging.getLogger("c")
    logconsole.propagate = False
    logconsole.setLevel(console_log_level)
    logconsole.addHandler(console_handler)


def setup_env() -> argparse.Namespace:
    r"""Setup the logger and parse the args.

    Returns:
        The parsed arguments.
    """
    # parse the command line arguments
    args = parse_arguments()

    # setup the loggers
    console_fmt_type = args.console_fmt_type
    console_log_level = args.console_log_level
    setup_logger(console_fmt_type=console_fmt_type, console_log_level=console_log_level)

    # build command string to repeat this run, useful to remember default values
    # if an option is a flag this does not work (can't just copy/paste), sorry
    recap = "python3 sample_logger.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"
    logg = logging.getLogger(f"c.{__name__}.setup_env")
    logg.info(recap)

    return args


def run_analyze_hist(args: argparse.Namespace) -> None:
    r"""Analyze the blink history.

    Args:
        args: The parsed cmdline arguments.
    """
    logg = logging.getLogger(f"c.{__name__}.run_analyze_hist")
    logg.setLevel("DEBUG")
    logg.debug("Starting run_analyze_hist")

    fireflies_num = args.fireflies_num
    fireflies_comm = args.fireflies_comm

    hist_name = f"histBlinkID_{fireflies_num}_{fireflies_comm}.txt"
    hist_path = Path(__file__).absolute().parent / hist_name
    logg.debug(f"hist_path: {hist_path}")

    minutes = 0
    new_minute = False

    # if you see a 0 sec and new_minute is True
    # increment the minutes and set it to False
    # if you see a 59 sec set new_minute to True again

    blinks = []

    with hist_path.open() as f:
        for line in f:
            pieces = line.rstrip().split(",")
            # this was the last line cut off badly
            if len(pieces) != 3 or len(pieces[2]) == 0:
                break
            # get the data as ints
            sec = int(pieces[1])
            millisec = int(pieces[2])
            recap = f"sec: {sec} millisec {millisec}"

            if new_minute and sec == 0:
                new_minute = False
                minutes += 1

            if not new_minute and sec == 59:
                new_minute = True

            blink_millisec = minutes * 60 * 1000 + sec * 1000 + millisec
            blinks.append(blink_millisec)

            recap += f" blink_millisec {blink_millisec}"
            # logg.debug(recap)

    blinks_np = np.array(blinks)

    # compute the freq
    values, counts = np.unique(blinks_np, return_counts=True)
    logg.debug(f"values: {values}")
    logg.debug(f"counts: {counts}")

    fig, ax = plt.subplots(1, 1)
    ax.plot(values, counts, marker="x", linestyle="none")
    fig.tight_layout()

    # bin_wid = 20
    bin_wid = 50
    bin_edges = np.arange(blinks_np.min(), blinks_np.max() + bin_wid, bin_wid)
    logg.debug(f"bin_edges.shape: {bin_edges.shape}")

    fig, ax = plt.subplots(1, 1)
    ax.hist(values, bin_edges, weights=counts)
    fig.tight_layout()

    plt.show()


if __name__ == "__main__":
    args = setup_env()
    run_analyze_hist(args)
