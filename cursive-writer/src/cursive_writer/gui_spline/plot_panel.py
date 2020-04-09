import logging
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from cursive_writer.utils.color_utils import fmt_cn


class PlotPanel(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        super().__init__(parent, *args, **kwargs)

        logg.debug(f"self: {self}")

        # setup grid for this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the plot
        self.fig = Figure(dpi=80, facecolor=(0.75, 0.75, 0.75))

        # self.ax0 = self.fig.add_axes((0.05, 0.05, 0.90, 0.90))
        self.ax0 = self.fig.add_axes((0, 0, 1, 1))
        # facecolor=(0.75, 0.75, 0.75), frameon=True
        self.ax0.set_axis_off()
        self.ax0.set_facecolor((0.75, 0.75, 0.75))

        # self.ax0.plot([1, 4, 6, 2, 6, 3], ls="", marker=".")

        # add the plot to a FigureCanvasTkAgg and grid that
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # this are in many tutorials but create problem in the grid
        # and the plot gets drawn without calling draw...
        # self.canvas.draw()
        # self.fig.canvas.draw()

        logg.debug(f"self.canvas.get_tk_widget(): {self.canvas.get_tk_widget()}")

    def update_plot(self, x, y):
        self.ax0.clear()
        self.ax0.plot(x, y, ls="", marker=".", color='k')
        self.canvas.draw()
