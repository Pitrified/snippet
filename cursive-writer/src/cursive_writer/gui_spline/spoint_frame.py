import logging
import tkinter as tk
from timeit import default_timer as timer

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn


class FrameSPoint(tk.Frame):
    def __init__(self, parent, name, spoint, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

        super().__init__(parent, *args, **kwargs)

        self.name = name
        self.spoint = spoint
