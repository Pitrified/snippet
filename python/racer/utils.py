import logging
import pygame
import numpy as np

from math import cos
from math import sin
from math import radians

# functions to create our resources


def load_image(name, colorkey=None):
    #  fullname = os.path.join(data_dir, name)
    fullname = name
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print("Cannot load image:", fullname)
        raise SystemExit(str(geterror()))
    #  image = image.convert()
    # load the image with an alpha channel
    image = image.convert_alpha()

    # this is not needed if the image is already transparent
    # if it is on a background, it defines the color in the corner as colorkey
    # and it will be left transparent
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def getMyLogger(logger_name, log_level="DEBUG"):
    """returns the logger requested
    """
    logg = logging.getLogger(logger_name)
    logg.setLevel(log_level)
    return logg


def compute_rot_matrix(theta):
    """compute the rotation matrix for angle theta in degrees
    """
    logg = getMyLogger(f"c.{__name__}.compute_rot_matrix", 'INFO')

    theta = radians(theta)
    ct = cos(theta)
    st = sin(theta)
    rot_mat = np.array(((ct, -st), (st, ct)))
    logg.debug(f"rot_mat = {rot_mat}")

    return rot_mat
