import logging
import pygame

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

def getMyLogger(logger_name, log_level='DEBUG'):
    logg = logging.getLogger(logger_name)
    logg.setLevel(log_level)
    return logg
