import argparse
import logging
import pygame

import numpy as np

from random import seed
from timeit import default_timer as timer

from pygame.sprite import spritecollide

from racer_env import RacerEnv
from racer_racer import RacerCar
from racer_map import RacerMap
from utils import getMyLogger


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--template_images",
        type=str,
        default="./{}",
        help="where to save/find the images",
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
    log_format_module = "%(name)s: %(message)s"
    #  log_format_module = "%(message)s"

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
    if args.seed == -1:
        myseed = 1
        myseed = int(timer() * 1e9 % 2 ** 32)
    else:
        myseed = args.seed
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


def run_racer_main(args):
    """mainloop of the game

    adapted from https://www.pygame.org/docs/tut/chimp.py.html
    and https://www.pygame.org/docs/tut/ChimpLineByLine.html
    """
    logg = logging.getLogger(f"c.{__name__}.run_racer_main")

    template_images = args.template_images
    fps = args.fps

    pygame.init()
    # size is (int, int) tuple
    field_size = (900, 900)
    # unpack the field size for clarity
    field_wid, field_hei = field_size
    sidebar_size = (300, field_hei)
    sidebar_wid, sidebar_hei = sidebar_size
    total_size = (field_wid + sidebar_wid, field_hei)

    screen = pygame.display.set_mode(total_size)
    pygame.display.set_caption("Racer")

    # Create The playing field
    field = pygame.Surface(field_size)
    # convert() changes the pixel format
    # https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert
    field = field.convert()
    #  field.fill((250, 250, 250))
    field.fill((0, 0, 0))

    # Put Text On The field, Centered
    if not pygame.font:
        logg.error("You need fonts to put text on the screen")

    # create a new Font object (from a file if you want)
    font = pygame.font.Font(None, 36)

    # draw the field on the screen
    screen.blit(field, (0, 0))

    # create the sidebar
    sidebar = pygame.Surface(sidebar_size)
    sidebar = sidebar.convert()
    sidebar.fill((80, 80, 80))

    # render() draws the text on a Surface
    text_title = font.render("Drive safely", 1, (255, 255, 255))
    # somewhere here there is a nice drawing of rect pos
    # https://dr0id.bitbucket.io/legacy/pygame_tutorial01.html
    # the pos is relative to the surface you blit to
    textpos_title = text_title.get_rect(centerx=sidebar_wid / 2)

    # draw the text on the sidebar
    sidebar.blit(text_title, textpos_title)

    val_delta = 50
    speed_text_hei = 200
    text_speed = font.render("Speed:", 1, (255, 255, 255))
    textpos_speed = text_speed.get_rect(center=(sidebar_wid / 2, speed_text_hei))
    sidebar.blit(text_speed, textpos_speed)
    speed_val_hei = speed_text_hei + val_delta

    direction_text_hei = 300
    text_direction = font.render("Direction:", 1, (255, 255, 255))
    textpos_direction = text_direction.get_rect(
        center=(sidebar_wid / 2, direction_text_hei)
    )
    sidebar.blit(text_direction, textpos_direction)
    direction_val_hei = direction_text_hei + val_delta

    # draw the sidebar on the screen
    screen.blit(sidebar, (field_wid, 0))

    # update the display (linked with screen)
    pygame.display.flip()

    # Prepare Game Objects
    clock = pygame.time.Clock()

    #  racer = RacerCar(template_images, field_wid // 2, field_hei // 2)
    racer = RacerCar(template_images, 100, 100)

    rmap = RacerMap(field_wid, field_hei)
    # draw map on the field, it is static, so there is no need to redraw it every time
    rmap.draw(field)

    # draw the map first, the car on top
    #  allsprites = pygame.sprite.RenderPlain((rmap, racer))
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

        hits = spritecollide(racer, rmap, dokill=False)
        logg.debug(f"hitting {hits}")
        hit_directions = []
        hit_sid = []
        for segment in hits:
            logg.debug(f"hit segment with id {segment.sid}")
            hit_directions.append(rmap.seg_info[segment.sid][0])
            hit_sid.append(segment.sid)
        racer._compute_reward(hit_directions, hit_sid)

        # Draw Everything again, every frame
        # the field already has the road drawn
        screen.blit(field, (0, 0))

        # draw all moving sprites (the car) on the screen
        allsprites.draw(screen)
        # if you draw on the field you can easily leave a track
        #  allsprites.draw(field)

        # draw the sidebar template
        screen.blit(sidebar, (field_wid, 0))
        # draw the updated numbers

        pygame.display.flip()

    pygame.quit()


def run_racer_new(args):
    """
    """
    logg = getMyLogger(f"c.{__name__}.run_racer_new")
    logg.debug(f"Start run_racer_new")

    template_images = args.template_images
    fps = args.fps

    # clock for interactive play
    clock = pygame.time.Clock()

    field_wid = 900
    field_hei = 900

    racer_env = RacerEnv(field_wid, field_hei, template_images)

    # add the car to the list of sprites to draw
    #  allsprites = pygame.sprite.RenderPlain((racer_env.racer_car))

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
            racer_env.step("right")
        elif keys[pygame.K_a]:
            racer_env.step("left")
        elif keys[pygame.K_w]:
            racer_env.step("up")
        elif keys[pygame.K_x]:
            racer_env.step("down")
        elif keys[pygame.K_q]:
            racer_env.step("upleft")
        elif keys[pygame.K_e]:
            racer_env.step("upright")
        elif keys[pygame.K_z]:
            racer_env.step("downleft")
        elif keys[pygame.K_c]:
            racer_env.step("downright")
        else:
            racer_env.step("nop")

        racer_env.update_display()


if __name__ == "__main__":
    args = setup_env()
    #  run_racer_main(args)
    run_racer_new(args)
