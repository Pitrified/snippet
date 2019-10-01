import logging

import numpy as np
from numpy.random import normal as npnorm

from timeit import default_timer as timer
from random import randint
from random import random
from math import pi, sin, cos
from math import radians


class Agent:
    def __init__(self, dod_map, bias, scale, step_len, x=None, y=None, d=None):
        """Create a doodling agent, that will draw on dod_map

        bias controls the tightness of the curvature
        step_len is the length of a step
        specific position and direction can be provided
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.dod_map = dod_map
        self.map_shape = dod_map.mappa.shape
        self.bias = bias
        self.scale = scale
        self.step_len = step_len

        pad = 10
        if x is None:
            #  self.x = randint(pad, self.map_shape[0] - pad)
            self.x = 50
        else:
            self.x = x

        if y is None:
            #  self.y = randint(pad, self.map_shape[1] - pad)
            self.y = self.map_shape[1] // 2
        else:
            self.y = y

        if d is None:
            #  self.d = random() * 360
            self.d = 90*3
        else:
            self.d = d

    def step(self):
        """Take a step after turning slightly

        The direction change is a normal with a small bias to one side
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.step")
        #  logg.info(f"Step")

        dir_delta = npnorm(loc=self.bias, scale=self.scale)
        logg.debug(f"sampled {dir_delta:.3f}")
        logg.debug(f"pre  x {self.x} y {self.y} d {self.d:.3f}")

        self.d += dir_delta

        rd = radians(self.d)

        #  self.x += int(cos(rd) * self.step_len)
        #  self.y += int(sin(rd) * self.step_len)
        self.x += cos(rd) * self.step_len
        self.y += sin(rd) * self.step_len
        logg.debug(f"post x {self.x} y {self.y} d {self.d:.3f}")

        self.dod_map.mappa[int(self.x)][int(self.y)] = 255
