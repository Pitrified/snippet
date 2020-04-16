import logging
from tkinter import ttk

from cursive_writer.utils.color_utils import fmt_cn


class FrameSPoint(ttk.Frame):
    def __init__(self, parent, name, spoint, *args, **kwargs):
        """Shows info for a spline point

        spoint: the point, saved in absolute coordinate
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start')} init")

        super().__init__(parent, *args, **kwargs)

        self.name = name
        self.spoint = spoint
        # this point is the same object as the one all the way in model.all_SP Observable
        logg.debug(f"id(self.spoint): {id(self.spoint)}")

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the element
        #  pos_str = f"{spoint.ori_deg:6.1f} @ ({spoint.x:6.1f}, {spoint.y:6.1f})"
        #  self.pos_lab = ttk.Label(self, text=pos_str, style="sp_pos.sp_info.TLabel")
        self.pos_lab = ttk.Label(self, style="sp_pos.sp_info.TLabel")
        self.update_label()

        # grid the element in the frame
        self.pos_lab.grid(row=0, column=0, sticky="nsew")

    def register_scroll_func(self, func):
        logg = logging.getLogger(f"c.{__class__.__name__}.register_scroll_func")
        #  logg.setLevel("TRACE")
        logg.trace(f"{fmt_cn('Register')} scroll function")

        self.pos_lab.bind("<4>", func)
        self.pos_lab.bind("<5>", func)
        self.pos_lab.bind("<MouseWheel>", func)

    def register_on_content(self, kind, func):
        """Bind event kind to func, on the label inside the frame
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.register_on_content")
        #  logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('register_on_content')}")

        self.pos_lab.bind(kind, func)

    def on_enter(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_enter")
        #  logg.setLevel("TRACE")
        logg.trace(f"{fmt_cn('Enter')} FrameSPoint {self.spoint.spid}")
        logg.trace(f"Event {event} fired by {event.widget}")
        spid = event.widget.spoint.spid
        logg.trace(f"event.widget.spoint.spid: {spid}")

        self.event_generate("<<sp_frame_enter>>")
        self.set_state("active")

    def on_leave(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_leave")
        #  logg.setLevel("TRACE")
        logg.trace(f"{fmt_cn('Leave')} FrameSPoint {self.spoint.spid}")

        self.event_generate("<<sp_frame_leave>>")
        self.set_state("!active")

    def on_button1_press(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_button1_press")
        #  logg.setLevel("TRACE")
        logg.trace(f"Clicked {fmt_cn('Button-1')} on FrameSPoint {self.spoint.spid}")

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
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('set_state')} {the_state}")

        self.pos_lab.state([the_state])

    def update_label(self):
        """Updates the text in the label based on the current spoint
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_label")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('update_label')}")

        pos_str = f"{self.spoint.ori_deg:6.1f} @"
        pos_str += f" ({self.spoint.x:6.1f}, {self.spoint.y:6.1f})"
        self.pos_lab["text"] = pos_str
