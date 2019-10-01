import logging
import cv2

import numpy as np

from timeit import default_timer as timer


class DoodleMap:
    """Thin wrapper around a np array
    """

    def __init__(self, width, height):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start init")

        self.width = width
        self.height = height

        self.mappa = np.zeros((width, height), dtype=np.uint8)

    def save(self, path_output):
        """Save the current map in path_output
        """
        cv2.imwrite(path_output, self.mappa)

    def tprint(self):
        for row in self.mappa:
            for val in row:
                print(f"{val: 4d}", end='')
            print()
