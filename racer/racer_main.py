import argparse
import logging
import pygame

import numpy as np

from random import seed
from timeit import default_timer as timer

from racer_racer import Racer


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--out_file_sprite",
        type=str,
        default="car.bmp",
        help="where to save the car image",
    )

    parser.add_argument("-fps", "--fps", type=int, default=1, help="frame per second")
    parser.add_argument("-s", "--seed", type=int, default=-1, help="random seed to use")

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


def run_racer_main(out_file_sprite, fps):
    """mainloop of the game

    adapted from https://www.pygame.org/docs/tut/chimp.py.html
    and https://www.pygame.org/docs/tut/ChimpLineByLine.html
    """
    logg = logging.getLogger(f"c.{__name__}.run_racer_main")

    pygame.init()
    screen = pygame.display.set_mode((900, 900))
    pygame.display.set_caption("Racer")

    # Create The Backgound
    background = pygame.Surface(screen.get_size())
    # convert() changes the pixel format
    # https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert
    background = background.convert()
    #  background.fill((250, 250, 250))
    background.fill((0, 0, 0))

    # Put Text On The Background, Centered
    if pygame.font:
        # create a new Font object (from a file)
        font = pygame.font.Font(None, 36)
        # render() draws the text on a Surface
        text = font.render("Drive safely", 1, (128, 128, 128))
        # somewhere here there is a nice drawing of rect pos
        # https://dr0id.bitbucket.io/legacy/pygame_tutorial01.html
        textpos = text.get_rect(centerx=background.get_width() / 2)
        # draw the text on the background
        background.blit(text, textpos)

    # draw the background on the screen
    screen.blit(background, (0, 0))
    # update the display (linked with screen)
    pygame.display.flip()

    # Prepare Game Objects
    clock = pygame.time.Clock()
    racer = Racer(out_file_sprite, screen.get_size()[0] // 2, screen.get_size()[1] // 2)
    allsprites = pygame.sprite.RenderPlain((racer))

    # Main Loop
    going = True
    while going:
        clock.tick(fps)
        logg.debug(f"    New frame")

        # Handle Input Events
        # https://stackoverflow.com/a/22099654
        for event in pygame.event.get():
            logg.debug(f"Handling event {event}")
            if event.type == pygame.QUIT:
                going = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    going = False
            logg.debug(f"Done handling")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            racer.step("right")
        elif keys[pygame.K_a]:
            racer.step("left")
        elif keys[pygame.K_w]:
            racer.step("up")
        elif keys[pygame.K_x]:
            racer.step("down")
        elif keys[pygame.K_q]:
            racer.step("upleft")
        elif keys[pygame.K_e]:
            racer.step("upright")
        elif keys[pygame.K_z]:
            racer.step("downleft")
        elif keys[pygame.K_c]:
            racer.step("downright")
        else:
            racer.step("nop")

        # manually update the racer, pass the action in step
        #  allsprites.update()

        # Draw Everything again, every frame
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()


def main():
    setup_logger()

    args = parse_arguments()

    # setup seed value
    if args.seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.seed
    seed(myseed)
    np.random.seed(myseed)

    out_file_sprite = args.out_file_sprite
    fps = args.fps

    recap = f"python3 racer_main.py"
    recap += f" --out_file_sprite {out_file_sprite}"
    recap += f" --fps {fps}"
    recap += f" --seed {myseed}"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    run_racer_main(out_file_sprite, fps)


if __name__ == "__main__":
    main()
