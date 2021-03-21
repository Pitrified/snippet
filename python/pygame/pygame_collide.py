import argparse
import logging

import numpy as np

from random import seed
from timeit import default_timer as timer


from pygame import Rect
from pygame.sprite import Group
from pygame.sprite import Sprite
from pygame.sprite import spritecollide


def parse_arguments():
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
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')

    # example log line
    logg = logging.getLogger(f"c.{__name__}.setup_logger")
    logg.debug(f"Done setting up logger")


def setup_env():
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.rand_seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.rand_seed
    seed(myseed)
    np.random.seed(myseed)

    # build command string to repeat this run
    recap = f"python3 lab03_main.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_pygame_collide(args):
    """Test if spritecollide works without pygame.init() called

    Rect(left, top, width, height) -> Rect
    """
    logg = logging.getLogger(f"c.{__name__}.run_pygame_collide")
    logg.info(f"Start run_pygame_collide")

    c_rect = Rect(10, 20, 40, 80)
    logg.debug(f"c_rect {c_rect}")
    car = Sprite()
    car.rect = c_rect
    logg.debug(f"car {car}")

    segments = []
    for i in range(5):
        new_seg = Sprite()
        s_rect = Rect(i*30, i*50, 40, 80)
        new_seg.rect = s_rect
        segments.append(new_seg)

    mmap = Group()
    for seg in segments:
        mmap.add(seg)
    logg.debug(f"mmap {mmap}")

    hits = spritecollide(car, mmap, dokill=False)
    for segment in hits:
        #  logg.debug(f"hit segment with id {segment.s_id}")
        #  logg.debug(f"hit segment {segment}")
        logg.debug(f"hit segment with rect {segment.rect}")

if __name__ == "__main__":
    args = setup_env()
    run_pygame_collide(args)
