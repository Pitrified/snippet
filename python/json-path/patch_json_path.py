"""Patch to encode/decode Path."""
import argparse
import json
import logging
from pathlib import Path
import typing as ty


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

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(
    console_fmt_type: str = "m",
    console_log_level: str = "WARN",
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


def as_path(dct) -> ty.Any:
    r"""Decode a string into a Path."""
    logg = logging.getLogger(f"c.{__name__}.as_path")
    logg.setLevel("DEBUG")
    logg.debug("Start as_path")

    if "__path_patch__" in dct:
        return Path(dct["path_string"])
    return dct


class PathEncoder(json.JSONEncoder):
    def default(self, obj) -> ty.Any:
        r"""Encode a Path into a dict with a string representation."""
        logg = logging.getLogger(f"c.{__name__}.default")
        logg.setLevel("DEBUG")
        logg.debug("Start default")

        if isinstance(obj, Path):
            return {"__path_patch__": True, "path_string": str(obj)}
        return json.JSONEncoder.default(self, obj)


def run_patch_json_path(args: argparse.Namespace) -> None:
    r"""Test the patch to encode/decode Path.

    Args:
        args: The parsed cmdline arguments.
    """
    logg = logging.getLogger(f"c.{__name__}.run_patch_json_path")
    logg.setLevel("DEBUG")
    logg.debug("Starting run_patch_json_path")

    some_path = Path("test_path") / "to" / "save.txt"
    some_dict = {"my_path": some_path}

    logg.debug(f"some_dict: {some_dict}")

    dict_str = json.dumps(some_dict, indent=4, cls=PathEncoder)

    logg.debug(dict_str)

    new_dict = json.loads(dict_str, object_hook=as_path)
    logg.debug(f"new_dict: {new_dict}")


if __name__ == "__main__":
    args = setup_env()
    run_patch_json_path(args)
