import argparse
import logging

# from timeit import default_timer as timer
from timeit import timeit
import numpy as np  # type: ignore


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


def setup_timeit() -> str:
    r"""MAKEDOC: what is setup_timeit doing?"""
    logg = logging.getLogger(f"c.{__name__}.setup_timeit")
    # logg.setLevel("DEBUG")
    logg.debug("Start setup_timeit")

    setup = """\
import numpy as np
a = np.zeros((3, 5, 5), dtype=np.int32)
a[0][2, 1] = 1
a[1][3, 4] = 1
a[2][4, 0] = 1
b = np.zeros((3,), dtype=np.bool)
b[1] = 1
not_b = np.logical_not(b)
"""
    return setup


def run_einsum(args: argparse.Namespace) -> None:
    r"""Experiments with Einstein summation

    https://ajcr.net/Basic-guide-to-einsum/
    https://chintak.github.io/2013/07/31/numpy-the-tricks-of-the-trade-part-ii/
    """
    logg = logging.getLogger(f"c.{__name__}.run_einsum")
    logg.setLevel("DEBUG")
    logg.debug("Starting run_einsum")

    a = np.zeros((3, 5, 5), dtype=np.int32)
    a[0][2, 1] = 1
    a[1][3, 4] = 1
    a[2][4, 0] = 1
    logg.debug(f"\na: {a.shape}\n{a}")

    aT = np.transpose(a, axes=[1, 2, 0])
    logg.debug(f"\naT: {aT.shape}\n{aT}")

    b = np.zeros((3,), dtype=np.bool)
    b[1] = 1
    logg.debug(f"\nb: {b.shape}\n{b}")

    not_b = np.logical_not(b)
    logg.debug(f"\nnot_b: {not_b.shape}\n{not_b}")

    # es = np.einsum("ijk,i->jk", a, b)
    # logg.debug(f"\nes: {es.shape}\n{es}")

    es = np.einsum("ijk,i->jk", a, not_b)
    logg.debug(f"\nes: {es.shape}\n{es}")

    # sumax = np.sum(a, axis=0, where=b)
    # sumax = np.sum(aT, axis=2, where=b)
    sumax = np.sum(aT, axis=2, where=not_b)
    # sumax = np.sum(a, axis=0)
    logg.debug(f"\nsumax: {sumax.shape}\n{sumax}")

    # - If `a` is an N-D array and `b` is a 1-D array, it is a sum product over
    #   the last axis of `a` and `b`.
    # So it does not work without transposing a before
    # dotab = np.dot(a, b)
    # dotab = np.dot(aT, b)
    # logg.debug(f"\ndotab: {dotab.shape}\n{dotab}")
    # sumdot = np.sum(dotab, axis=0)
    # logg.debug(f"\nsumdot: {sumdot.shape}\n{sumdot}")
    dotab = np.dot(aT, not_b)
    logg.debug(f"\ndotab: {dotab.shape}\n{dotab}")

    # ip = np.inner(a, b)
    # ip = np.inner(aT, b)
    # logg.debug(f"\nip: {ip.shape}\n{ip}")
    ip = np.inner(aT, not_b)
    logg.debug(f"\nip: {ip.shape}\n{ip}")

    setup = setup_timeit()
    stmt = 'np.einsum("ijk,i->jk", a, not_b)'
    print(timeit(stmt=stmt, setup=setup))

    stmt = 'aT = np.transpose(a, axes=[1, 2, 0]); ip = np.inner(aT, not_b)'
    print(timeit(stmt=stmt, setup=setup))

    stmt = 'aT = np.transpose(a, axes=[1, 2, 0]); ip = np.dot(aT, not_b)'
    print(timeit(stmt=stmt, setup=setup))


if __name__ == "__main__":
    args = setup_env()
    run_einsum(args)
