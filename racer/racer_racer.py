import argparse
import logging
import numpy as np

from random import seed
from timeit import default_timer as timer
from math import cos
from math import sin
from math import radians

from PIL import Image
from PIL import ImageDraw

from pygame import display
from pygame.sprite import Sprite

from utils import load_image


class Racer(Sprite):
    """Experimental car to understand the agent

    Will be rewritten as proper gym env
    """

    def __init__(self, pos_x, pos_y, direction=0):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start init")

        super().__init__()

        self.out_file_sprite = "car.bmp"
        self._create_sprite_image()
        self.image, self.rect = load_image(self.out_file_sprite)
        logg.debug(f"Rect di car {self.rect}")

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.precise_x = pos_x
        self.precise_y = pos_y

        # car heading, degrees
        self.direction = direction
        self.dir_step = 3

        self.speed = 0
        self.speed_step = 1
        # viscous drag coefficient
        self.drag_coeff = 0.5

        logg.debug(f"Pos x {self.pos_x} y {self.pos_y} dir {self.direction}")
        self.rect.center = self.pos_x, self.pos_y

    def step(self, action):
        """Perform the action

        left-rigth: change steering
        up-down: accelerate/brake
        combination of the above
        do nothing
        """
        logg = logging.getLogger(f"c.{__name__}.step")
        logg.debug(f"Doing action {action}")

        if action == "up":
            self.speed += self.speed_step
        elif action == "down":
            self.speed -= self.speed_step
            # MAYBE it can go in reverse?
            if self.speed < 0:
                self.speed = 0
        elif action == "right":
            self.direction -= self.dir_step
        elif action == "left":
            self.direction += self.dir_step

        pos_x_d = cos(radians(self.direction)) * self.speed
        pos_y_d = sin(radians(self.direction)) * self.speed

        self.precise_x += pos_x_d
        self.precise_y += pos_y_d

        self.pos_x = int(self.precise_x)
        self.pos_y = int(self.precise_y)
        self.rect.center = self.pos_x, self.pos_y

    def _create_sprite_image(self):
        self.size = 60, 40
        img1 = Image.new("RGBA", self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img1)
        wheel_len = 7
        wheel_wid = 6
        mid = wheel_wid / 2
        delta = -3
        # top left wheel
        self._draw_oval(draw, 15 + delta + mid, 10 - mid, wheel_wid, wheel_len, "grey")
        # top right wheel
        self._draw_oval(
            draw, 45 - (delta + mid + wheel_len), 10 - mid, wheel_wid, wheel_len, "grey"
        )
        # bottom left
        self._draw_oval(draw, 15 + delta + mid, 30 - mid, wheel_wid, wheel_len, "grey")
        # bottom right wheel
        self._draw_oval(
            draw, 45 - (delta + mid + wheel_len), 30 - mid, wheel_wid, wheel_len, "grey"
        )
        # body
        self._draw_oval(draw, 15, 10, 20, 30, "red")

        # TODO triangle for windshield

        # MAYBE can the saving be avoided
        img1.save(self.out_file_sprite, "bmp")

    def _draw_oval(self, draw, top, left, width, length, color):
        """draw an oval, top left is for the rectangle

        circle rect circle
        draw.rectangle(((15, 10), (45, 30)), fill="red")
        draw.ellipse(((5, 10), (25, 30)), fill="red")
        draw.ellipse(((35, 10), (55, 30)), fill="red")
        top 15 left 10 width 20 length 30
        """
        # make width even to simplify things
        if width % 2 != 0:
            width += 1
        mid = width / 2
        draw.rectangle(((top, left), (top + length, left + width)), fill=color)
        draw.ellipse(((top - mid, left), (top + mid, left + width)), fill=color)
        draw.ellipse(
            ((top + length - mid, left), (top + length + mid, left + width)), fill=color
        )
