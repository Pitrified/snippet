import logging
import tkinter as tk

from side_panel import SidePanel
from plot_panel import PlotPanel


class View:
    def __init__(self, root):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        self.root = root

        # setup grid for root
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)

        # create children widget
        self.plot_panel = PlotPanel(self.root, bg="SeaGreen1")
        self.side_panel = SidePanel(self.root, bg="dark orange")

        # grid children widget
        self.plot_panel.grid(row=0, column=0, sticky="nsew")
        self.side_panel.grid(row=0, column=1, sticky="nsew")
