import logging

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class PlotPanel(tk.Frame):
    def __init__(self, *args, **kwargs):
        log = logging.getLogger(f"{__name__}.init")
        log.debug('Start init')

        tk.Frame.__init__(self, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(7.5, 4), dpi=80)
        self.ax0 = self.fig.add_axes((0.05, .05, .90, .90), facecolor=(.75, .75, .75), frameon=False)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")
        self.canvas.draw()

    def plot_changed(self, res):
        self.ax0.clear()
        self.ax0.contourf(res["x"], res["y"], res["z"])
        self.fig.canvas.draw()
