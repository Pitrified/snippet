import numpy as np
import logging

from observable import Observable


class Model:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.xpoint = 200
        self.ypoint = 200

        self.expX = Observable(1)
        self.expY = Observable(1)

        self.funcType = Observable("cos")

        self.res = Observable(None)

    def calculate(self):
        log = logging.getLogger(f"c.{__name__}.calculate")
        log.info("Calculating")

        x, y = np.meshgrid(
            np.linspace(-5, 5, self.xpoint), np.linspace(-5, 5, self.ypoint)
        )

        if self.funcType.get() == "cos":
            z = np.cos(x ** self.expX.get() * y ** self.expY.get())
        elif self.funcType.get() == "sin":
            z = np.sin(x ** self.expX.get() * y ** self.expY.get())
        else:
            log.error(f"Unrecognized funcType {self.funcType.get()}")

        self.res.set({"x": x, "y": y, "z": z})

    def setExpX(self, value):
        log = logging.getLogger(f"c.{__name__}.setExpX")
        log.info(f"Setting exp X to {value}")

        self.expX.set(value)

        self.calculate()

    def setExpY(self, value):
        log = logging.getLogger(f"c.{__name__}.setExpY")
        log.info(f"Setting exp Y to {value}")

        self.expY.set(value)

        self.calculate()

    def setFunc(self, funcType):
        log = logging.getLogger(f"c.{__name__}.setFunc")
        log.info(f"Setting funcType to {funcType}")

        self.funcType.set(funcType)
        self.calculate()
