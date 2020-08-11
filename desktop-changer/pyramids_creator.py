import argparse
import logging

from pathlib import Path
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
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


def get_font_size(text, max_hei, font_name="DejaVuSans.ttf"):
    """Finds the font size so that the text is as big as requested

    https://stackoverflow.com/a/4902713
    """
    # logg = logging.getLogger(f"c.{__name__}.get_font_size")
    # logg.debug("Start get_font_size")

    fontsize = 30
    font = ImageFont.truetype(font_name, fontsize)

    while font.getsize(text)[1] < max_hei:
        fontsize += 1
        font = ImageFont.truetype(font_name, fontsize)
        # logg.debug(f"fontsize: {fontsize}")

    fontsize -= 1
    font = ImageFont.truetype(font_name, fontsize)

    return font


def draw_image(img_path, rgb_sky, rgb_sunny, rgb_shade, rgb_background, img_size):
    """TODO: what is draw_image doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_image")
    # logg.debug("Start draw_image")

    # create the empty image
    im = Image.new("RGB", img_size, rgb_background)

    # create the draw object for the image
    draw = ImageDraw.Draw(im)

    # box for the pie
    pie_x = img_size[0] * 0.1
    pie_y = img_size[1] * 0.2
    pie_l = img_size[0] * 0.35
    # left = 200
    # top = 200
    # right = 600
    # bottom = 600
    # pie_box = (left, top, right, bottom)
    pie_box = (pie_x, pie_y, pie_x + pie_l, pie_y + pie_l)

    # draw the pie
    slice_1 = 130
    slice_2 = 43
    slice_3 = 58
    draw.pieslice(pie_box, start=slice_1, end=slice_2, fill=rgb_sky)
    draw.pieslice(pie_box, start=slice_2, end=slice_3, fill=rgb_shade)
    draw.pieslice(pie_box, start=slice_3, end=slice_1, fill=rgb_sunny)

    # square dimensions
    sq_x = img_size[0] * 0.6  # x of the left side of the squares
    sq_y = img_size[1] * 0.25  # y of the top square
    sq_l = img_size[0] * 0.05  # size of the squares
    sq_space = sq_l / 2  # space between the squares

    # squares
    sq_1 = (sq_x, sq_y, sq_x + sq_l, sq_y + sq_l)
    draw.rectangle(sq_1, fill=rgb_sky)
    sq_2 = (sq_x, sq_y + sq_l + sq_space, sq_x + sq_l, sq_y + sq_l * 2 + sq_space)
    draw.rectangle(sq_2, fill=rgb_sunny)
    sq_3 = (
        sq_x,
        sq_y + sq_l * 2 + sq_space * 2,
        sq_x + sq_l,
        sq_y + sq_l * 3 + sq_space * 2,
    )
    draw.rectangle(sq_3, fill=rgb_shade)

    # font
    font = get_font_size("Sky", sq_space)

    # text shift
    te_s = sq_space

    # text
    te_1 = (sq_1[0] + te_s + sq_l, sq_1[1] + sq_space / 2)
    draw.text(te_1, "Sky", fill="white", font=font)
    te_2 = (sq_2[0] + te_s + sq_l, sq_2[1] + sq_space / 2)
    draw.text(te_2, "Sunny side of pyramid", fill="white", font=font)
    te_3 = (sq_3[0] + te_s + sq_l, sq_3[1] + sq_space / 2)
    draw.text(te_3, "Shady side of pyramid", fill="white", font=font)

    # image number
    img_num = img_path.name[-6:-4]
    num_pos = (sq_1[0], sq_1[1] + sq_space * 10)
    draw.text(num_pos, img_num, fill="white", font=font)

    # TODO: stars at night!

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


def hsv360_to_rgb255(hsv360):
    """TODO: what is hsv360_to_rgb255 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.hsv360_to_rgb255")
    # logg.debug("Start hsv360_to_rgb255")

    hsv = (hsv360[0] / 360, hsv360[1] / 100, hsv360[2] / 100)
    rgb = hsv_to_rgb(*hsv)
    rgb = tuple(int(c * 255) for c in rgb)
    return rgb


def get_colors():
    """TODO: what is get_colors doing?

    0/6 000 red
    1/6 060 yellow
    2/6 120 green
    3/6 180 cyan
    4/6 240 blue
    5/6 300 magenta
    """
    # logg = logging.getLogger(f"c.{__name__}.get_colors")
    # logg.debug("Start get_colors")

    hsv_all_sky = {
        0: (0, 100, 100),
        1: (30, 100, 100),
        2: (60, 100, 100),
        3: (90, 100, 100),
        4: (120, 100, 100),
        5: (150, 100, 100),
        6: (180, 100, 100),
        7: (210, 100, 100),
        8: (240, 100, 100),
        9: (270, 100, 100),
        10: (300, 100, 100),
        11: (330, 100, 100),
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

    hsv_all_sky = {
        0: (220, 30, 10),
        1: (240, 40, 20),
        2: (250, 40, 40),
        3: (270, 40, 40),
        4: (290, 50, 50),
        5: (290, 50, 60),
        # 5: (290, 50, 60),
        6: (290, 50, 70),
        # 6: (250, 70, 70),
        7: (240, 80, 80),
        8: (230, 90, 80),
        9: (230, 90, 90),
        10: (220, 90, 90),
        11: (220, 90, 100),
        12: (220, 100, 100),
        13: (240, 90, 90),
        14: (240, 90, 80),
        15: (240, 90, 70),
        16: (240, 90, 60),
        17: (240, 90, 55),
        18: (260, 70, 50),
        # 19: (270, 40, 40),
        # 19: (20, 90, 55),
        19: (30, 100, 60),
        # 20: (280, 40, 30),
        # 20: (20, 90, 55),
        20: (270, 40, 40),
        21: (250, 40, 30),
        22: (240, 40, 20),
        23: (220, 30, 10),
    }

    hsv_all_sunny = {
        0: (0, 50, 100),
        1: (30, 50, 100),
        2: (60, 50, 100),
        3: (90, 50, 100),
        4: (120, 50, 100),
        5: (150, 50, 100),
        6: (180, 50, 100),
        7: (210, 50, 100),
        8: (240, 50, 100),
        9: (270, 50, 100),
        10: (300, 50, 100),
        11: (330, 50, 100),
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

    hsv_all_sunny = {
        0: (40, 90, 25),
        1: (40, 90, 25),
        2: (40, 90, 30),
        3: (40, 90, 35),
        # 4: (10, 90, 40),
        4: (30, 90, 40),
        5: (20, 90, 40),
        # 5: (340, 90, 50),
        6: (10, 90, 40),
        # 6: (350, 90, 60),
        7: (30, 90, 65),
        8: (35, 90, 75),
        9: (40, 90, 85),
        10: (40, 90, 90),
        11: (40, 100, 90),
        12: (40, 100, 100),
        13: (40, 100, 90),
        14: (40, 90, 75),
        15: (40, 90, 65),
        16: (40, 90, 60),
        17: (40, 90, 55),
        18: (32, 90, 50),  # 35
        19: (28, 90, 45),  # 30
        20: (22, 90, 40),  # 25
        21: (33, 90, 35),  # 35
        22: (40, 90, 30),
        23: (40, 90, 25),
    }

    hsv_all_shade = {
        k: (v[0], v[1], max(v[2] - 30, 0)) for k, v in hsv_all_sunny.items()
    }

    return hsv_all_sky, hsv_all_sunny, hsv_all_shade


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

    img_size = (1600, 900)
    rgb_background = (12, 12, 12)

    img_folder = Path("./out_pyramids")
    logg.debug(f"img_folder: {img_folder}")
    if not img_folder.exists():
        img_folder.mkdir(parents=True)

    hsv_all_sky, hsv_all_sunny, hsv_all_shade = get_colors()

    for i in range(24):
        img_name = f"pyr_{i:02d}.jpg"
        img_path = img_folder / img_name

        rgb_sky = hsv360_to_rgb255(hsv_all_sky[i])
        rgb_sunny = hsv360_to_rgb255(hsv_all_sunny[i])
        rgb_shade = hsv360_to_rgb255(hsv_all_shade[i])

        draw_image(img_path, rgb_sky, rgb_sunny, rgb_shade, rgb_background, img_size)


if __name__ == "__main__":
    args = setup_env()
    run_pyramids_creator(args)
