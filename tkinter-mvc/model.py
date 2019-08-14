import numpy as np
import logging

from observable import Observable

class Model:
    def __init__(self):
        log = logging.getLogger(f"{__name__}.init")
        log.debug('Start init')

        self.xpoint = 200
        self.ypoint = 200
        self.res = Observable(None)

    def calculate(self):
        x, y = np.meshgrid(
            np.linspace(-5, 5, self.xpoint), np.linspace(-5, 5, self.ypoint)
        )
        z = np.cos(x ** 2 * y ** 3)
        self.res.set({"x": x, "y": y, "z": z})
