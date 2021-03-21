import logging

import tkinter as tk

from model import Model
from view import View


class Controller:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.root = tk.Tk()

        # initialize model
        self.model = Model()

        self.model.res.addCallback(self.PlotChanged)
        # you do NOT register a callback on expX; the Model.res changes, so the
        # view gets updated by the callback bound to Model.res
        #  self.model.expX.addCallback(self.PlotChanged)

        # initialize view
        self.view = View(self.root)

        # bind callbacks from user input
        self.view.side_panel.funcOpt.bind("<<ComboboxSelected>>", self.SetFuncCombo)
        self.view.side_panel.selectedFunc.trace("w", self.SetFuncVar)
        self.view.side_panel.plotBut.config(command=self.PlotDraw)
        self.view.side_panel.scaleX.config(command=self.SetScaleX)
        self.view.side_panel.scaleY.config(command=self.SetScaleY)

        log.info("Done init, calculate the plot for the first time")
        self.model.calculate()

    def run(self):
        """Start the app and run the mainloop
        """
        log = logging.getLogger(f"c.{__name__}.run")
        log.info("Running controller\n")

        self.root.title("Tkinter MVC example")
        #  self.root.deiconify()
        self.root.mainloop()

    def PlotDraw(self):
        log = logging.getLogger(f"c.{__name__}.PlotDraw")
        log.info("PlotDraw fired, a button was pressed")

        self.model.calculate()

    def SetFuncVar(self, *args):
        log = logging.getLogger(f"c.{__name__}.SetFuncVar")
        log.setLevel("INFO")
        log.info("SetFuncVar fired")
        log.debug(f"Args received: {args} type {type(args)}")
        # I don't like hardcoding the view structure in the callback
        log.debug(f"{self.view.side_panel.selectedFunc.get()}")

    def SetFuncCombo(self, event):
        log = logging.getLogger(f"c.{__name__}.SetFuncCombo")
        log.setLevel("INFO")
        log.info("SetFuncCombo fired")
        log.debug(f"Event received {event}")
        log.debug(f"python type {type(event)} tkinter type {event.type}")
        log.debug(f"widget {event.widget}")
        log.debug(f"widget.get() {event.widget.get()}")

        value = event.widget.get()
        self.model.setFunc(value)

    def SetScaleX(self, event):
        log = logging.getLogger(f"c.{__name__}.SetScaleX")
        log.setLevel("INFO")
        log.info("SetScaleX fired, a slider was moved")
        log.debug(f"Event received {event} type {type(event)}")

        value = int(event)
        self.model.setExpX(value)

    def SetScaleY(self, event):
        log = logging.getLogger(f"c.{__name__}.SetScaleY")
        log.setLevel("INFO")
        log.info("SetScaleY fired, a slider was moved")
        log.debug(f"Event received {event} type {type(event)}")

        value = int(event)
        self.model.setExpY(value)

    def PlotChanged(self, data):
        log = logging.getLogger(f"c.{__name__}.PlotChanged")
        log.info("PlotChanged fired, an Observable changed")

        self.view.plot_panel.plot_changed(data)
