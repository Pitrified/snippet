import logging
import tkinter as tk
from tkinter import ttk
from timeit import default_timer as timer

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.spline_point import SplinePoint


class FrameSPoint(tk.Frame):
    def __init__(self, parent, name, spoint, *args, **kwargs):
        """Shows info for a spline point

        spoint: the point, saved in absolute coordinate
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

        super().__init__(parent, *args, **kwargs)

        self.name = name
        self.spoint = spoint

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the element
        pos_str = f"{spoint.ori_deg:6.1f} @ ({spoint.x:5.1f}, {spoint.y:5.1f})"
        self.pos_lab = ttk.Label(self, text=pos_str, style="sp_pos.TLabel")

        # grid the element in the frame
        self.pos_lab.grid(row=0, column=0, sticky="nsew")
