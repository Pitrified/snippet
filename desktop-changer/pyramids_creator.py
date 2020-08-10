import argparse
import logging

from pathlib import Path
from PIL import Image, ImageDraw
from colorsys import hsv_to_rgb


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


def setup_env():
    setup_logger()

    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = "python3 pyramids_creator.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def draw_image(
    img_path, rgb_sky, rgb_bright, rgb_shade, rgb_background, img_size, img_num=None
):
    """TODO: what is draw_image doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_image")
    # logg.debug("Start draw_image")

    # create the empty image
    im = Image.new("RGB", img_size, rgb_background)

    # create the draw object for the image
    draw = ImageDraw.Draw(im)

    # box for the pie
    left = 200
    top = 200
    right = 600
    bottom = 600
    pie_box = (left, top, right, bottom)

    # draw the pie
    slice_1 = 130
    slice_2 = 43
    slice_3 = 58
    draw.pieslice(pie_box, start=slice_1, end=slice_2, fill=rgb_sky)
    draw.pieslice(pie_box, start=slice_2, end=slice_3, fill=rgb_shade)
    draw.pieslice(pie_box, start=slice_3, end=slice_1, fill=rgb_bright)

    # squares

    # text

    # image number

    # save the image
    im.save(img_path, quality=95)


def hsv_to_rgb255(hsv):
    """TODO: what is hsv_to_rgb255 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.hsv_to_rgb255")
    # logg.debug("Start hsv_to_rgb255")

    rgb = hsv_to_rgb(*hsv)
    rgb = tuple(int(c * 255) for c in rgb)
    return rgb


def hsv180_to_rgb255(hsv180):
    """TODO: what is hsv180_to_rgb255 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.hsv180_to_rgb255")
    # logg.debug("Start hsv180_to_rgb255")

    hsv = tuple(c / 180 for c in hsv180)
    rgb = hsv_to_rgb(*hsv)
    rgb = tuple(int(c * 255) for c in rgb)
    return rgb


def get_colors():
    """TODO: what is get_colors doing?

    0/6 000 red
    1/6 030 yellow
    2/6 060 green
    3/6 090 cyan
    4/6 120 blue
    5/6 150 magenta
    """
    # logg = logging.getLogger(f"c.{__name__}.get_colors")
    # logg.debug("Start get_colors")

    hsv_all_sky = {
        0: (0, 180, 180),
        1: (30, 180, 180),
        2: (60, 180, 180),
        3: (90, 180, 180),
        4: (120, 180, 180),
        5: (150, 180, 180),
        6: (0, 0, 0),
        7: (0, 0, 0),
        8: (0, 0, 0),
        9: (0, 0, 0),
        10: (0, 0, 0),
        11: (0, 0, 0),
        12: (0, 0, 0),
        13: (0, 0, 0),
        14: (0, 0, 0),
        15: (0, 0, 0),
        16: (0, 0, 0),
        17: (0, 0, 0),
        18: (0, 0, 0),
        19: (0, 0, 0),
        20: (0, 0, 0),
        21: (0, 0, 0),
        22: (0, 0, 0),
        23: (0, 0, 0),
    }

    hsv_all_bright = {
        0: (0, 0, 0),
        1: (0, 0, 0),
        2: (0, 0, 0),
        3: (0, 0, 0),
        4: (0, 0, 0),
        5: (0, 0, 0),
        6: (0, 0, 0),
        7: (0, 0, 0),
        8: (0, 0, 0),
        9: (0, 0, 0),
        10: (0, 0, 0),
        11: (0, 0, 0),
        12: (0, 0, 0),
        13: (0, 0, 0),
        14: (0, 0, 0),
        15: (0, 0, 0),
        16: (0, 0, 0),
        17: (0, 0, 0),
        18: (0, 0, 0),
        19: (0, 0, 0),
        20: (0, 0, 0),
        21: (0, 0, 0),
        22: (0, 0, 0),
        23: (0, 0, 0),
    }

    hsv_all_shade = {
        0: (0, 0, 0),
        1: (0, 0, 0),
        2: (0, 0, 0),
        3: (0, 0, 0),
        4: (0, 0, 0),
        5: (0, 0, 0),
        6: (0, 0, 0),
        7: (0, 0, 0),
        8: (0, 0, 0),
        9: (0, 0, 0),
        10: (0, 0, 0),
        11: (0, 0, 0),
        12: (0, 0, 0),
        13: (0, 0, 0),
        14: (0, 0, 0),
        15: (0, 0, 0),
        16: (0, 0, 0),
        17: (0, 0, 0),
        18: (0, 0, 0),
        19: (0, 0, 0),
        20: (0, 0, 0),
        21: (0, 0, 0),
        22: (0, 0, 0),
        23: (0, 0, 0),
    }

    return hsv_all_sky, hsv_all_bright, hsv_all_shade


def run_pyramids_creator(args):
    """TODO: What is pyramids_creator doing?

    Photos
    https://www.jetsoncreative.com/mac-dynamic-desktop-store/catalina-mix-mac
    https://sites.google.com/site/amilockerhub/home/time-lapse-image-travelcode
    https://videohive.net/item/mountain-time-lapse-from-day-to-night/25352583
    https://metro.co.uk/2015/05/12/haunting-time-lapse-photos-show-iconic-buildings-transition-from-day-to-night-5192792/
    """
    logg = logging.getLogger(f"c.{__name__}.run_pyramids_creator")
    logg.debug("Starting run_pyramids_creator")

    img_size = (1200, 900)
    rgb_background = (12, 12, 12)

    img_folder = Path("./out_pyramids")
    logg.debug(f"img_folder: {img_folder}")
    if not img_folder.exists():
        img_folder.mkdir(parents=True)

    hsv_all_sky, hsv_all_bright, hsv_all_shade = get_colors()

    for i in range(6):
        img_name = f"pyr_{i:02d}.jpg"
        img_path = img_folder / img_name

        rgb_sky = hsv180_to_rgb255(hsv_all_sky[i])
        rgb_bright = hsv180_to_rgb255(hsv_all_bright[i])
        rgb_shade = hsv180_to_rgb255(hsv_all_shade[i])

        draw_image(img_path, rgb_sky, rgb_bright, rgb_shade, rgb_background, img_size)


if __name__ == "__main__":
    args = setup_env()
    run_pyramids_creator(args)
