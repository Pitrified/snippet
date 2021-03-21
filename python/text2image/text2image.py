import argparse
import logging

from random import seed as rseed
from timeit import default_timer as timer

from PIL import Image, ImageDraw, ImageFont


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--img_out_path",
        type=str,
        default="hp.jpg",
        help="path to output image to use",
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
    rseed(myseed)

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 text2image.py"
    for a, v in args._get_kwargs():
        if a == "rand_seed":
            recap += f" --rand_seed {myseed}"
        else:
            recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def text_wrap(text, font, max_width):
    lines = []

    # split the text by newlines to get single lines
    for line in text.split("\n"):
        # If the width of the line is smaller than image width we don't
        # need to split it, just add it to the lines array
        if font.getsize(line)[0] <= max_width:
            lines.append(line)

        else:
            # split the line by spaces to get words
            words = line.split(" ")

            i = 0
            while i < len(words):
                line = ""
                while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                    line = line + words[i] + " "
                    i += 1
                if line == "":
                    # the first word considered is already longer than max_width:
                    # add it anyway, the word will be chopped
                    line = words[i]
                    i += 1
                # when the line gets longer than the max width do not append the word,
                # add the line to the lines array
                lines.append(line)
    return lines


def text2image(width, height, text, img_out_path, margin_top=20, margin_left=20):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.text2image")
    logg.debug(f"Starting text2image")

    back_color = (255, 255, 255)
    text_color = (0, 0, 0)

    # create empty Image object
    image = Image.new("RGB", (width, height), back_color)

    # initialise the drawing context with the image object as background
    draw = ImageDraw.Draw(image)

    # create font object with the font file and specify desired size
    # this is arial on Ubuntu
    font = ImageFont.truetype(
        "/usr/share/fonts/opentype/freefont/FreeSans.otf", size=45
    )

    max_width = width - 2 * margin_left
    line_height = font.getsize("hg")[1]

    x = margin_left
    y = margin_top

    lines = text_wrap(text, font, max_width)
    for line in lines:
        logg.debug(f"{line}")
        draw.text((x, y), line, fill=text_color, font=font)
        y += line_height

    image.save("output.png")
    image.save("optimized.png", optimize=True, quality=20)


def run_text2image(args):
    """

    https://haptik.ai/tech/putting-text-on-image-using-python/
    https://haptik.ai/tech/putting-text-on-images-using-python-part2/
    """
    logg = logging.getLogger(f"c.{__name__}.run_text2image")
    logg.debug(f"Starting run_text2image")

    img_out_path = args.img_out_path
    width = 600
    height = 800
    text = "Sample text 1st line."
    text += "\nSample text hella longer line, some would say this is too long"
    text += " but I disagree: it is just long enough."
    text += "\nSample text 3rd line:"
    text += " this line on the other end, is a bit too short."
    text += "\nNow consider the following line:"
    text += "\nSupercalifragilisticexpialidocious"
    text += "\nCould have gone better."

    text2image(width, height, text, img_out_path)


if __name__ == "__main__":
    args = setup_env()
    run_text2image(args)
