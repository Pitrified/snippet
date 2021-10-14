import argparse
import logging
from pathlib import Path

from cursive_writer.gui_spline.draw_controller import Controller
from cursive_writer.utils.setup import setup_logger


def parse_arguments():
    """Setup CLI interface"""
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="hp.jpg",
        help="Path to input image to use",
    )

    parser.add_argument(
        "-t", "--thickness", type=int, default=10, help="Thickness of the drawn letter"
    )

    parser.add_argument(
        "-cs", "--colorscheme", type=str, default="snow", help="Colorscheme to use"
    )

    parser.add_argument(
        "-lld",
        "--log_level_debug",
        type=str,
        default="INFO",
        help="LogLevel for the debugging logger",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    parser.add_argument(
        "-llt",
        "--log_level_type",
        type=str,
        default="m",
        help="Message format for the debugging logger",
        choices=["anlm", "nlm", "lm", "nm", "m"],
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_env():
    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 gui_main.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    # setup the logger with specified debug level
    setup_logger(args.log_level_debug, args.log_level_type)

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_gui_main(args):
    """"""
    logg = logging.getLogger(f"c.{__name__}.run_gui_main")
    logg.debug(f"Starting run_gui_main")

    path_input = args.path_input
    main_dir = Path(__file__).resolve().parent
    logg.debug(f"main_dir: {main_dir}")
    image_dir = main_dir.parent / "images"
    logg.debug(f"image_dir: {image_dir}")
    pf_input_image = image_dir / path_input
    logg.debug(f"pf_input_image: {pf_input_image}")
    data_dir = main_dir.parent / "data"
    logg.debug(f"data_dir: {data_dir}")

    c = Controller(pf_input_image, data_dir, args.thickness, args.colorscheme)
    c.run()


if __name__ == "__main__":
    args = setup_env()
    run_gui_main(args)
