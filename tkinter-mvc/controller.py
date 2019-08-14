import logging

import tkinter as tk

from model import Model
from view import View


class Controller:
    def __init__(self):
        log = logging.getLogger(f"c.{__name__}.init")
        log.debug('Start init')

        self.root = tk.Tk()

        self.model = Model()

        self.model.res.addCallback(self.PlotChanged)

        self.view = View(self.root)

        self.view.side_panel.plotBut.config(command=self.PlotDraw)

    def run(self):
        self.root.title("Tkinter MVC example")
        self.root.deiconify()
        self.root.mainloop()

    def PlotDraw(self):
        self.model.calculate()

    def PlotChanged(self, data):
        self.view.plot_panel.plot_changed(data)
