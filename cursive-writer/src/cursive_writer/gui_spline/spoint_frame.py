import logging
import tkinter as tk
from tkinter import ttk
from timeit import default_timer as timer

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.spline_point import SplinePoint


class FrameSPoint(ttk.Frame):
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

    def register_scroll_func(self, func):
        logg = logging.getLogger(f"c.{__class__.__name__}.register_scroll_func")
        #  logg.setLevel("TRACE")
        logg.trace(f"{fmt_cn('Register', 'start')} scroll function")

        self.pos_lab.bind("<4>", func)
        self.pos_lab.bind("<5>", func)
        self.pos_lab.bind("<MouseWheel>", func)

    def register_on_content(self, kind, func):
        """Bind event kind to func, on the label inside the frame
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.register_on_content")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('register_on_content', 'start')}")

        self.pos_lab.bind(kind, func)

    def on_enter(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_enter")
        #  logg.setLevel("TRACE")
        logg.debug(f"{fmt_cn('Enter', 'start')} FrameSPoint {self.spoint.spid}")
        logg.trace(f"Event {event} fired by {event.widget}")
        spid = event.widget.spoint.spid
        logg.trace(f"event.widget.spoint.spid: {spid}")

        # the virtual event is left for future needs, MAYBE compute some things
        # on the fly between active and selected? Who knows. Draw a spline?
        #  self.event_generate("<<sp_frame_enter>>")
        self.set_state("active")

    def on_leave(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_leave")
        #  logg.setLevel("TRACE")
        logg.debug(f"{fmt_cn('Leave', 'start')} FrameSPoint {self.spoint.spid}")

        #  self.event_generate("<<sp_frame_leave>>")
        self.set_state("!active")

    def on_button1_press(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_button1_press")
        #  logg.setLevel("TRACE")
        logg.debug(
            f"Clicked {fmt_cn('Button-1', 'start')} on FrameSPoint {self.spoint.spid}"
        )

        self.event_generate("<<sp_frame_btn1_press>>")

    def set_state(self, the_state):
        """Sets the state of the internal frame elements

        For weird reasons you cannot pass a string directly, as it will raise
        '_tkinter.TclError: Invalid state name a' where a is the first letter
        of the string, so it is iterating over it
        Apparently some documentations are wrong, only iterables can be sent as
        statespec
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.set_state")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('set_state', 'start')} {the_state}")

        self.pos_lab.state([the_state])
