import logging
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from cursive_writer.utils.color_utils import fmt_cn


class PlotPanel(ttk.Frame):
    def __init__(self, parent, style_option, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        super().__init__(parent, *args, **kwargs)

        self.style_option = style_option

        logg.log(5, f"self: {self}")

        # setup grid for this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.facecolor = self.style_option["bg_container_rgb"]

        # create the plot
        self.fig = Figure(dpi=80, facecolor=self.facecolor)
        # self.fig = Figure(dpi=80, facecolor='k')

        self.ax0 = self.fig.add_axes((0, 0, 1, 1))
        # facecolor=(0.75, 0.75, 0.75), frameon=True
        self.ax0.set_axis_off()
        self.ax0.set_facecolor(self.facecolor)

        # add the plot to a FigureCanvasTkAgg and grid that
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # this are in many tutorials but create problem in the grid
        # and the plot gets drawn without calling draw anyway...
        # self.canvas.draw()
        # self.fig.canvas.draw()

        logg.log(5, f"self.canvas.get_tk_widget(): {self.canvas.get_tk_widget()}")

    def update_plot(self, x, y):
        self.ax0.clear()

        # self.ax0.plot(x, y, ls="", marker=".", color="k")
        # self.ax0.set_facecolor(self.facecolor)
        self.ax0.plot(x, y, ls="", marker=".", color=self.facecolor)
        self.ax0.set_facecolor("k")

        self.canvas.draw()
