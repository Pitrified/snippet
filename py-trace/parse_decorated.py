import argparse
import logging
from pathlib import Path
import re
import typing as ty
from dataclasses import dataclass

# from timeit import default_timer as timer
# import numpy as np  # type: ignore


@dataclass
class FunctionInfo:
    """Class to keep track of function calls."""

    name: str
    indent: int
    repeat: int

    def get_indent_str(self):
        this_indent = "    " * self.indent
        repeat_str = f" x{self.repeat}" if self.repeat > 1 else ""
        return f"{this_indent}{self.name}{repeat_str}"


def parse_arguments() -> argparse.Namespace:
    r"""Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "--trace_name",
        type=str,
        default="tracedec.txt",
        help="Input trace report to parse.",
    )

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


def run_parse_decorated(args: argparse.Namespace) -> None:
    r"""MAKEDOC: What is parse_decorated doing?

    Parse the output of decorate_trace.py
    """
    logg = logging.getLogger(f"c.{__name__}.run_parse_decorated")
    # logg.setLevel("DEBUG")
    logg.debug("Starting run_parse_decorated")

    trace_name = args.trace_name

    this_file_folder = Path(__file__).absolute().parent
    trace_path = this_file_folder / trace_name

    re_start = re.compile("S: (.*?)$")
    re_end = re.compile("E: (.*?), T: (.*?) s$")

    active_func = []

    indent_str = "    "
    indent_level = 0

    logg.info("\nCall list:")

    call_list: ty.List[FunctionInfo] = [FunctionInfo("start", 0, 0)]

    start_prefix = ""
    # start_prefix = "S: "
    end_prefix = "E: "

    with open(trace_path) as ftp:
        for line in ftp:
            line = line.rstrip()

            # the regex could be used to find the match, and would accept different log
            # styles, but I think this is faster
            if line.startswith("S"):
                match = re_start.search(line)

                if match is None:
                    logg.warning(f"{line} starts with Start but does not match.")
                    continue

                # the name of the function just called
                funcname = match[1]

                # print info
                this_indent = indent_str * indent_level
                logg.info(f"{this_indent}{start_prefix}{funcname}")

                # save in the active_func stack
                active_func.append(funcname)

                # save in the call_list
                last_func = call_list[-1]
                if last_func.name == funcname:
                    last_func.repeat += 1
                else:
                    call_list.append(FunctionInfo(funcname, indent_level, 1))

                indent_level += 1

            elif line.startswith("E"):
                match = re_end.search(line)

                if match is None:
                    logg.warning(f"{line} starts with End but does not match.")
                    continue

                funcname = match[1]
                # functime = match[2]

                # check that the last active_func corresponds to the exiting one
                lastfunc = active_func[-1]
                logg.debug(f"lastfunc: {lastfunc}")
                assert lastfunc == funcname

                active_func.pop()

                this_indent = indent_str * indent_level
                logg.debug(f"{this_indent}{end_prefix}{funcname}")

                indent_level -= 1

    # print the function still on stack if the run was interrupted
    if len(active_func) > 0:
        logg.info("\nStack list:")
        for funcname in reversed(active_func):
            indent_level -= 1
            this_indent = indent_str * indent_level
            logg.info(f"{this_indent}{funcname}")

    for fi in call_list:
        logg.info(f"{fi.get_indent_str()}")


if __name__ == "__main__":
    args = setup_env()
    run_parse_decorated(args)
