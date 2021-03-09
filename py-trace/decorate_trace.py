import argparse
import logging

from example_class import ExampleClass
from timefunc import timefunc_modulename


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

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel: str = "WARN", msg_type: str = "m") -> None:
    r"""Setup logger that outputs to console for the module"""

    # setup the format string
    format_types = {}
    format_types["anlm"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    format_types["nlm"] = "%(name)s - %(levelname)s: %(message)s"
    format_types["lm"] = "%(levelname)s: %(message)s"
    format_types["nm"] = "%(name)s: %(message)s"
    format_types["m"] = "%(message)s"
    formatter = logging.Formatter(format_types[msg_type])

    # setup the console handler with the formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # setup the console logger with the console handler
    logconsole = logging.getLogger("c")
    logconsole.propagate = False
    logconsole.setLevel(logLevel)
    logconsole.addHandler(console_handler)

    # setup the file handler
    file_handler = logging.FileHandler("decorate_trace.log", mode="w")
    file_handler.setFormatter(formatter)

    # setup the file logger with the file handler
    logfile = logging.getLogger("f")
    logfile.propagate = False
    logfile.setLevel("DEBUG")
    logfile.addHandler(file_handler)


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


@timefunc_modulename(__name__)
def fnoreturn():
    pass


@timefunc_modulename(__name__)
def fd(d):
    return d + 12


@timefunc_modulename(__name__)
def fc(c):
    for _ in range(3):
        c += fd(c)
    return c + 12


@timefunc_modulename(__name__)
def fb(b):
    return fc(b) * 3


@timefunc_modulename(__name__)
def fa(a, b):
    fnoreturn()
    a = fd(a)
    temp = fc(a) + fb(b)
    ec = ExampleClass()
    ec.classfunc()
    return temp


@timefunc_modulename(__name__)
def run_decorate_trace(args: argparse.Namespace) -> None:
    r"""MAKEDOC: What is decorate_trace doing?"""
    logg = logging.getLogger(f"c.{__name__}.run_decorate_trace")
    # logg.setLevel("DEBUG")
    logg.debug("Starting run_decorate_trace")

    a = fa(2, 4)
    fnoreturn()
    fd(a)
    fb(a)


if __name__ == "__main__":
    args = setup_env()
    run_decorate_trace(args)
