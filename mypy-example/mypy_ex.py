import argparse
import logging
import math
import numpy as np  # type: ignore

from random import seed as rseed
from timeit import default_timer as timer


def parse_arguments() -> argparse.Namespace:
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

    parser.add_argument(
        "-s", "--rand_seed", type=int, default=-1, help="random seed to use"
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel: str = "DEBUG") -> None:
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def setup_env() -> argparse.Namespace:
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.rand_seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.rand_seed
    rseed(myseed)
    np.random.seed(myseed)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 mypy_ex.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


class OrientedPoint:
    def __init__(self, x: float, y: float, ori_deg: float) -> None:
        """Create a point with orientation

        point (x,y) with orientation in degrees, ranging [-180, 180)
        """
        self.x = x
        self.y = y
        self.set_ori_deg(ori_deg)

    def set_ori_deg(self, ori_deg: float) -> None:
        """Set the orientation of the points in degrees

        Updates the orientation in radians and slope as well
        """
        # save orientation in [-180, 180) range
        if ori_deg > 180:
            ori_deg -= 360
        if ori_deg <= -180:
            ori_deg += 360

        self.ori_deg = ori_deg
        # convert it to radians
        self.ori_rad = math.radians(self.ori_deg)
        # convert to slope of a line
        self.ori_slo = math.tan(self.ori_rad)

    def __repr__(self) -> str:
        the_repr_str = ""
        # the_repr_str += f"({self.x:.4f}, {self.y:.4f})"
        # the_repr_str += f" # {self.ori_deg:.4f}"
        the_repr_str += f"({self.x:}, {self.y:})"
        the_repr_str += f" # {self.ori_deg:}"
        return the_repr_str


class SplinePoint(OrientedPoint):
    """Spline Point: an OrientedPoint with additional info
    """

    def __init__(self, x: float, y: float, ori_deg: float, spid: int) -> None:
        """Create a point with orientation

        point (x,y) with orientation in degrees, ranging [-180, 180)
        spid: a unique integer identifier for the point
        """
        super().__init__(x, y, ori_deg)
        self.spid = spid

    def __repr__(self) -> str:
        the_repr_str = super().__repr__()
        the_repr_str += f" SPID: {self.spid}"
        return the_repr_str


def run_mypy_ex(args: argparse.Namespace) -> None:
    """TODO: What is mypy_ex doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_mypy_ex")
    logg.debug(f"Starting run_mypy_ex")

    op = OrientedPoint(0, 0, 0)
    logg.debug(f"op: {op}")

    sp = SplinePoint(0, 0, 0, 0)
    logg.debug(f"sp: {sp}")
    sp.spid = 4


if __name__ == "__main__":
    args = setup_env()
    run_mypy_ex(args)
