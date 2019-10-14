import logging

from timeit import default_timer as timer

from pygame.sprite import Group


class RacingMap(Group):
    """Map for a racer, as collection of rect

    Should be easy to do collision detection
    """

    def __init__(self):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Start init")

        super().__init__()

