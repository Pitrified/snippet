import argparse
import logging
from pathlib import Path
import re

# from timeit import default_timer as timer
# import numpy as np  # type: ignore


def parse_arguments() -> argparse.Namespace:
    r"""Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    default = "WARN"
    parser.add_argument(
        "-lld",
        "--log_level_debug",
        type=str,
        default=default,
        help=f"Level for the debugging logger, default {default}",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    default = "m"
    parser.add_argument(
        "-llt",
        "--log_level_type",
        type=str,
        default=default,
        help=f"Message format for the debugging logger, default {default}",
        choices=["anlm", "nlm", "lm", "nm", "m"],
    )

    parser.add_argument(
        "--trace_name",
        type=str,
        default="tracet.txt",
        help="Input trace report to parse.",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel: str = "WARN", msg_type: str = "m") -> None:
    r"""Setup logger that outputs to console for the module"""
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    if msg_type == "anlm":
        log_format_module = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    elif msg_type == "nlm":
        log_format_module = "%(name)s - %(levelname)s: %(message)s"
    elif msg_type == "lm":
        log_format_module = "%(levelname)s: %(message)s"
    elif msg_type == "nm":
        log_format_module = "%(name)s: %(message)s"
    else:
        log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)


def setup_env() -> argparse.Namespace:
    r"""Setup the logger and parse the args"""
    args = parse_arguments()
    setup_logger(args.log_level_debug, args.log_level_type)

    # build command string to repeat this run, useful to remember default values
    # FIXME if an option is a flag this does not work (can't just copy/paste), sorry
    recap = "python3 imagenet_preprocess.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_parse_trace(args: argparse.Namespace) -> None:
    r"""MAKEDOC: What is parse_trace doing?

    Parse the output of
    python -m trace --trace tracing.py > tracet.txt

    Should also parse
    python -m trace --trackcalls tracing.py
    To see which function calls which
    """
    logg = logging.getLogger(f"c.{__name__}.run_parse_trace")
    # logg.setLevel("DEBUG")
    logg.debug("Starting run_parse_trace")

    trace_name = args.trace_name

    this_file_folder = Path(__file__).absolute().parent
    # trace_path = this_file_folder / "tracet.txt"
    trace_path = this_file_folder / trace_name

    re_funccall = re.compile(" --- modulename: (.*?), funcname: (.*?)$")

    ignoremods = [
        "__init__",
        "_bootstrap",
        "_collections_abc",
        "_weakrefset",
        "abc",
        "argparse",
        "enum",
        "functools",
        "genericpath",
        "gettext",
        "locale",
        "os",
        "parse",
        "pathlib",
        "posixpath",
        "re",
        "shutil",
        "sre_compile",
        "sre_parse",
        "string",
        "threading",
        "trace",
        "traceback",
        "types",
        "weakref",
    ]

    ignorefuncs = [
        "time_closure",
        "timefunc",
    ]

    all_modules = set()
    all_func = set()

    with open(trace_path) as ftp:
        for line in ftp:
            if not line.startswith(" --- modulename"):
                continue
            line = line.rstrip()

            match = re_funccall.search(line)
            if match is None:
                logg.warning(f"{line} starts with --- modulename but does not match.")
                continue

            all_modules.add(match[1])
            if match[1] in ignoremods:
                continue
            logg.debug(f"match[1]: {match[1]}")

            all_func.add(match[2])
            if match[2] in ignorefuncs:
                continue
            logg.debug(f"match[2]: {match[2]}")

            logg.info(f"{line}")

    logg.debug("\nAll modules seen")
    for mod in sorted(all_modules):
        logg.debug(f"'{mod}',")

    logg.debug("\nAll functions seen")
    for func in sorted(all_func):
        logg.debug(f"'{func}',")


if __name__ == "__main__":
    args = setup_env()
    run_parse_trace(args)
