import argparse
import logging

from pathlib import Path
from PIL import Image  # type: ignore
from PIL import ImageDraw
from PIL import ImageFont
from colorsys import hsv_to_rgb
from colorsys import rgb_to_hsv
from random import random


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


def get_font_size(text, max_wid, font_name="DejaVuSans.ttf"):
    """Finds the font size so that the text is as big as requested

    https://stackoverflow.com/a/4902713
    """
    # logg = logging.getLogger(f"c.{__name__}.get_font_size")
    # logg.debug("Start get_font_size")

    fontsize = 30
    font = ImageFont.truetype(font_name, fontsize)

    while font.getsize(text)[0] < max_wid:
        fontsize += 1
        font = ImageFont.truetype(font_name, fontsize)
        # logg.debug(f"fontsize: {fontsize}")

    fontsize -= 1
    font = ImageFont.truetype(font_name, fontsize)

    return font


def hsv_to_rgb255(hsv):
    """Convert hsv (1, 1, 1) to rgb (255, 255, 255)
    """
    # logg = logging.getLogger(f"c.{__name__}.hsv_to_rgb255")
    # logg.debug("Start hsv_to_rgb255")

    rgb = hsv_to_rgb(*hsv)
    rgb255 = tuple(int(c * 255) for c in rgb)
    return rgb255


def hsv360_to_rgb255(hsv360):
    """Convert hsv (360, 100, 100) to rgb (255, 255, 255)
    """
    # logg = logging.getLogger(f"c.{__name__}.hsv360_to_rgb255")
    # logg.debug("Start hsv360_to_rgb255")

    hsv = (hsv360[0] / 360, hsv360[1] / 100, hsv360[2] / 100)
    rgb = hsv_to_rgb(*hsv)
    rgb255 = tuple(int(c * 255) for c in rgb)
    return rgb255


def rgb255_edit_as_hsv360(rgb255, dh360=0, ds100=0, dv100=0):
    """TODO: what is rgb255_edit_as_hsv360 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.rgb255_edit_as_hsv360")
    # logg.debug("Start rgb255_edit_as_hsv360")

    rgb = tuple(c / 255 for c in rgb255)
    hsv = rgb_to_hsv(*rgb)
    hsv360 = (hsv[0] * 360, hsv[1] * 100, hsv[2] * 100)
    hsv360 = (hsv360[0] + dh360, hsv360[1] + ds100, hsv360[2] + dv100)
    hsv360 = validate_hsv360(hsv360)
    return hsv360_to_rgb255(hsv360)


def validate_hsv360(hsv360):
    """TODO: what is validate_hsv360 doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.validate_hsv360")
    # logg.debug("Start validate_hsv360")

    hsv360 = (max(hsv360[0], 0), max(hsv360[1], 0), max(hsv360[2], 0))
    hsv360 = (min(hsv360[0], 360), min(hsv360[1], 100), min(hsv360[2], 100))
    return hsv360


def draw_circle(draw, c_color, center_x, center_y, radius):
    """TODO: what is draw_circle doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_circle")
    # logg.debug("Start draw_circle")

    c_box = (center_x - radius, center_y - radius, center_x + radius, center_y + radius)
    draw.ellipse(c_box, fill=c_color)


def draw_cloud(draw, c_left, c_top, c_size, c_color):
    """TODO: what is draw_cloud doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_cloud")
    # logg.debug("Start draw_cloud")

    # the bottom right circle
    draw_circle(draw, c_color, c_left + c_size / 2, c_top + c_size / 3, c_size / 5)
    # the bottom left circle
    draw_circle(draw, c_color, c_left - c_size / 2, c_top + c_size / 3, c_size / 5)
    # bottom line
    draw.rectangle(
        (
            c_left - c_size / 2,
            c_top + c_size / 3,
            c_left + c_size / 2,
            c_top + c_size / 3 + c_size / 5,
        ),
        fill=c_color,
    )
    draw_circle(draw, c_color, c_left - c_size / 3, c_top + c_size / 4, c_size / 4)
    draw_circle(draw, c_color, c_left - c_size / 8, c_top + c_size / 6, c_size / 3)
    draw_circle(draw, c_color, c_left + c_size / 6, c_top + c_size / 5, c_size / 4)


def draw_saturn(draw, s_left, s_top, s_size, sky_col):
    """TODO: what is draw_saturn doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_saturn")
    # logg.debug("Start draw_saturn")

    s_height = s_size * 0.35 / 2
    s_width = s_size / 2
    s_x_center = s_left + s_width
    s_y_center = s_top + s_height

    for i in range(4):
        ratio = 1 - (i * 0.18)
        s_col = "white" if i % 2 == 0 else sky_col
        tweak = 0 if i % 2 == 0 else 1
        ring_box = (
            s_x_center - s_width * ratio,
            s_y_center - s_height * ratio - tweak,
            s_x_center + s_width * ratio,
            s_y_center + s_height * ratio - tweak,
        )
        draw.ellipse(ring_box, fill=s_col)

    ratio = 0.7
    sat_box = (
        s_x_center - s_height * ratio,
        s_y_center - s_height * ratio - s_height * 0.0,
        s_x_center + s_height * ratio,
        s_y_center + s_height * ratio - s_height * 0.0,
    )
    draw.ellipse(sat_box, fill=(180, 180, 180))


def draw_star(draw, s_x_center, s_y_center, s_size):
    """TODO: what is draw_star doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_star")
    # logg.debug(f"Start draw_star")

    draw.polygon(
        (
            (s_x_center + s_size, s_y_center),
            (s_x_center + s_size / 6, s_y_center + s_size / 6),
            (s_x_center, s_y_center + s_size),
            (s_x_center - s_size / 6, s_y_center + s_size / 6),
            (s_x_center - s_size, s_y_center),
            (s_x_center - s_size / 6, s_y_center - s_size / 6),
            (s_x_center, s_y_center - s_size),
            (s_x_center + s_size / 6, s_y_center - s_size / 6),
        ),
        fill="white",
    )
    draw.line(
        (
            (s_x_center - s_size / 2, s_y_center + s_size / 2),
            (s_x_center + s_size / 2, s_y_center - s_size / 2),
        ),
        fill="white",
        width=1,
    )
    draw.line(
        (
            (s_x_center - s_size / 2, s_y_center - s_size / 2),
            (s_x_center + s_size / 2, s_y_center + s_size / 2),
        ),
        fill="white",
        width=1,
    )


def draw_image(img_path, rgb255, img_size, font, img_num):
    """Create the image and save it
    """
    # logg = logging.getLogger(f"c.{__name__}.draw_image")
    # logg.debug("Start draw_image")

    # create the empty image
    im = Image.new("RGB", img_size, rgb255["background"])

    # create the draw object for the image
    draw = ImageDraw.Draw(im)

    ###############
    ### PYRAMID ###
    ###############

    # box for the pie (left, top, right, bottom)
    pie_left = img_size[0] * 0.1  # x of the left of the pie
    pie_top = img_size[1] * 0.2  # y of the top of the pie
    pie_size = img_size[0] * 0.35  # size of the pie
    pie_box = (pie_left, pie_top, pie_left + pie_size, pie_top + pie_size)

    # draw the pie
    slice_1 = 130
    slice_2 = 43
    slice_3 = 58
    draw.pieslice(pie_box, start=slice_1, end=slice_2, fill=rgb255["sky"])

    # dist from midnight
    h_dist = 24 - img_num + 1 if img_num > 12 else img_num
    # logg.debug(f"h_dist: {h_dist}")

    # add the stars
    stars = (
        (4, 0.12, 0.42, 0.002),
        (4, 0.26, 0.61, 0.003),
        (4, 0.45, 0.45, 0.002),
        (4, 0.5, 0.35, 0.003),
        (4, 0.51, 0.2, 0.002),
        (4, 0.57, 0.1, 0.002),
        (4, 0.8, 0.41, 0.002),
        (4, 0.85, 0.59, 0.003),
        (5, 0.1, 0.6, 0.004),
        (5, 0.3, 0.3, 0.005),
        (5, 0.7, 0.6, 0.005),
        (5, 0.73, 0.33, 0.004),
        (6, 0.25, 0.55, 0.007),
        (6, 0.4, 0.2, 0.01),
        (6, 0.6, 0.4, 0.008),
    )
    for hd, rx, ry, rs in stars:
        if h_dist <= hd:
            star_x_center = pie_left + pie_size * rx
            star_y_center = pie_top + pie_size * ry
            star_size = img_size[0] * rs
            draw_star(draw, star_x_center, star_y_center, star_size)

    # add the clouds
    clo_color = rgb255_edit_as_hsv360(rgb255["sky"], ds100=-50, dv100=10)
    clo_left = pie_left + pie_size * 0.3 + pie_size * 0.1 * random()
    clo_top = pie_top + pie_size * 0.3 + pie_size * 0.1 * random()
    clo_size = img_size[0] * 0.05 + img_size[0] * 0.02 * random()
    draw_cloud(draw, clo_left, clo_top, clo_size, clo_color)

    clo_color = rgb255_edit_as_hsv360(rgb255["sky"], ds100=-40, dv100=10)
    clo_left = pie_left + pie_size * 0.6 + pie_size * 0.1 * random()
    clo_top = pie_top + pie_size * 0.54 + pie_size * 0.1 * random()
    clo_size = img_size[0] * 0.03 + img_size[0] * 0.02 * random()
    draw_cloud(draw, clo_left, clo_top, clo_size, clo_color)

    clo_color = rgb255_edit_as_hsv360(rgb255["sky"], ds100=-30, dv100=10)
    clo_left = pie_left + pie_size * 0.7 + pie_size * 0.1 * random()
    clo_top = pie_top + pie_size * 0.1 + pie_size * 0.1 * random()
    clo_size = img_size[0] * 0.08 + img_size[0] * 0.02 * random()
    draw_cloud(draw, clo_left, clo_top, clo_size, clo_color)

    # draw the pyramid late so that is in front of the clouds
    draw.pieslice(pie_box, start=slice_2, end=slice_3, fill=rgb255["shade"])
    draw.pieslice(pie_box, start=slice_3, end=slice_1, fill=rgb255["sunny"])

    # add saturn
    if h_dist <= 4:
        sat_left = pie_left + pie_size * 0.2
        sat_top = pie_top + pie_size * 0.2
        sat_size = img_size[0] * 0.015
        draw_saturn(draw, sat_left, sat_top, sat_size, rgb255["sky"])

    # draw a masked background to cut the circle precisely
    empty = Image.new("RGB", img_size, rgb255["background"])
    mask = Image.new("L", img_size, "white")
    circle = ImageDraw.Draw(mask)
    circle.ellipse(pie_box, fill="black")
    im.paste(empty, mask=mask)

    ##############
    ### LEGEND ###
    ##############

    # square dimensions
    sq_left = img_size[0] * 0.6  # x of the left side of the squares
    sq_top = img_size[1] * 0.25  # y of the top square
    sq_size = img_size[0] * 0.05  # size of the squares
    sq_space = sq_size / 2  # space between the squares

    # squares
    sq_1 = (sq_left, sq_top, sq_left + sq_size, sq_top + sq_size)
    draw.rectangle(sq_1, fill=rgb255["sky"])
    sq_2 = (
        sq_left,
        sq_top + sq_size + sq_space,
        sq_left + sq_size,
        sq_top + sq_size * 2 + sq_space,
    )
    draw.rectangle(sq_2, fill=rgb255["sunny"])
    sq_3 = (
        sq_left,
        sq_top + sq_size * 2 + sq_space * 2,
        sq_left + sq_size,
        sq_top + sq_size * 3 + sq_space * 2,
    )
    draw.rectangle(sq_3, fill=rgb255["shade"])

    # text shift
    te_s = sq_space

    # text
    te_1 = (sq_1[0] + te_s + sq_size, sq_1[1] + sq_space / 2)
    draw.text(te_1, "Sky", fill="white", font=font)
    te_2 = (sq_2[0] + te_s + sq_size, sq_2[1] + sq_space / 2)
    draw.text(te_2, "Sunny side of pyramid", fill="white", font=font)
    te_3 = (sq_3[0] + te_s + sq_size, sq_3[1] + sq_space / 2)
    draw.text(te_3, "Shady side of pyramid", fill="white", font=font)

    # image number
    # num_pos = (sq_1[0], sq_1[1] + sq_space * 10)
    # draw.text(num_pos, str(img_num), fill=(180, 180, 180), font=font)

    # TODO: stars at night!
    # TODO: saturn!
    # TODO: aliens!
    # TODO: colors/weather linked to the actual one via internet

    # save the image
    im.save(img_path, quality=95)


def get_colors():
    """Returns a dict with the hsv colors

    Labels:
        * sky
        * sunny side
        * shady side

    The hsv scale is (360, 100, 100)

    0/6 000 red
    1/6 060 yellow
    2/6 120 green
    3/6 180 cyan
    4/6 240 blue
    5/6 300 magenta
    """
    # logg = logging.getLogger(f"c.{__name__}.get_colors")
    # logg.debug("Start get_colors")

    hsv_all = {}

    hsv_all["sky"] = {
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

    hsv_all["sky"] = {
        0: (220, 30, 10),
        1: (240, 40, 20),
        2: (240, 40, 25),
        3: (240, 40, 30),
        4: (250, 40, 40),
        5: (270, 40, 40),
        6: (280, 50, 50),
        7: (250, 60, 70),
        8: (230, 70, 80),
        9: (230, 80, 90),
        10: (220, 90, 90),
        11: (220, 95, 100),
        12: (220, 100, 100),
        13: (240, 90, 90),
        14: (240, 90, 80),
        15: (240, 90, 70),
        16: (240, 90, 60),
        17: (240, 90, 55),
        18: (260, 70, 50),
        # 18: (340, 70, 50),
        19: (270, 40, 40),
        # 19: (10, 60, 45),
        # 19: (20, 90, 55),
        # 19: (30, 100, 60),
        # 20: (280, 40, 30),
        # 20: (20, 90, 55),
        20: (270, 40, 40),
        21: (250, 40, 30),
        22: (240, 40, 20),
        23: (220, 30, 10),
    }

    hsv_all["sunny"] = {
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

    hsv_all["sunny"] = {
        0: (40, 90, 25),
        1: (40, 90, 25),
        2: (40, 90, 30),
        3: (40, 90, 35),
        4: (30, 90, 40),
        5: (30, 90, 50),
        6: (30, 90, 60),
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

    hsv_all["shade"] = {
        k: (v[0], v[1], max(v[2] - 30, 10)) for k, v in hsv_all["sunny"].items()
    }

    return hsv_all


def run_pyramids_creator(args):
    """Setup and create the 24 images

    Photos
    https://www.jetsoncreative.com/mac-dynamic-desktop-store/catalina-mix-mac
    https://sites.google.com/site/amilockerhub/home/time-lapse-image-travelcode
    https://videohive.net/item/mountain-time-lapse-from-day-to-night/25352583
    https://metro.co.uk/2015/05/12/haunting-time-lapse-photos-show-iconic-buildings-transition-from-day-to-night-5192792/
    """
    logg = logging.getLogger(f"c.{__name__}.run_pyramids_creator")
    logg.debug("Starting run_pyramids_creator")

    # img_size = (1600, 900)
    img_size = (1920 * 2, 1080 * 2)

    # colors
    rgb255 = {}
    rgb255["background"] = (12, 12, 12)
    hsv_all = get_colors()

    # font
    text_width = img_size[0] * 0.25
    font = get_font_size("Shady side of pyramid", text_width)

    # save path
    img_folder = Path("./out_pyramids")
    logg.debug(f"img_folder: {img_folder}")
    if not img_folder.exists():
        img_folder.mkdir(parents=True)

    for i in range(24):
        img_name = f"pyr_{i:02d}.jpg"
        img_path = img_folder / img_name

        rgb255["sky"] = hsv360_to_rgb255(hsv_all["sky"][i])
        rgb255["sunny"] = hsv360_to_rgb255(hsv_all["sunny"][i])
        rgb255["shade"] = hsv360_to_rgb255(hsv_all["shade"][i])

        draw_image(img_path, rgb255, img_size, font, i)


if __name__ == "__main__":
    args = setup_env()
    run_pyramids_creator(args)
