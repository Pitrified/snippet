import logging

from timeit import default_timer as timer

# pygame
import pygame
from pygame.sprite import Sprite
from pygame.transform import rotate

# my files
from racer_racer import RacerCar
from racer_map import RacerMap
from utils import getMyLogger


class RacerEnv:
    """
    """

    def __init__(self, field_wid, field_hei):
        logg = getMyLogger(f"c.{__class__.__name__}.__init__")
        logg.debug(f"Start init")

        self.field_wid = field_wid
        self.field_hei = field_hei
        self.field_size = (self.field_wid, self.field_hei)

        self.sidebar_wid = 300
        self.sidebar_hei = self.field_hei
        self.sidebar_size = (self.sidebar_wid, self.sidebar_hei)

        self.total_wid = self.sidebar_wid + self.field_wid
        self.total_hei = self.field_hei
        self.total_size = (self.total_wid, self.total_hei)

        pygame.init()
        self.screen = pygame.display.set_mode(self.total_size)
        pygame.display.set_caption("Racer")

        # Create The playing field
        self.field = pygame.Surface(self.field_size)
        # convert() changes the pixel format
        # https://www.pygame.org/docs/ref/surface.html#pygame.Surface.convert
        self.field = self.field.convert()
        #  self.field.fill((250, 250, 250))
        self.field.fill((0, 0, 0))

        # draw the field on the screen
        self.screen.blit(self.field, (0, 0))

        # Put Text On The field, Centered
        if not pygame.font:
            logg.critical("You need fonts to put text on the screen")

        # create a new Font object (from a file if you want)
        self.main_font = pygame.font.Font(None, 36)

        self.setup_sidebar()

    def setup_sidebar(self):
        """
        """
        # create the sidebar
        self.sidebar = pygame.Surface(self.sidebar_size)
        self.sidebar = self.sidebar.convert()
        self.sidebar.fill((80, 80, 80))

        # render() draws the text on a Surface
        text_title = self.main_font.render("Drive safely", 1, (255, 255, 255))
        # somewhere here there is a nice drawing of rect pos
        # https://dr0id.bitbucket.io/legacy/pygame_tutorial01.html
        # the pos is relative to the surface you blit to
        textpos_title = text_title.get_rect(centerx=self.sidebar_wid / 2)

        # draw the text on the sidebar
        self.sidebar.blit(text_title, textpos_title)

        val_delta = 50
        speed_text_hei = 200
        text_speed = self.main_font.render("Speed:", 1, (255, 255, 255))
        textpos_speed = text_speed.get_rect(
            center=(self.sidebar_wid / 2, speed_text_hei)
        )
        self.sidebar.blit(text_speed, textpos_speed)
        speed_val_hei = speed_text_hei + val_delta

        direction_text_hei = 300
        text_direction = self.main_font.render("Direction:", 1, (255, 255, 255))
        textpos_direction = text_direction.get_rect(
            center=(self.sidebar_wid / 2, direction_text_hei)
        )
        self.sidebar.blit(text_direction, textpos_direction)
        direction_val_hei = direction_text_hei + val_delta

        # draw the sidebar on the screen
        self.screen.blit(self.sidebar, (self.field_wid, 0))
