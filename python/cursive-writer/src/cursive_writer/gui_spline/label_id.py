import logging
from tkinter import ttk

from cursive_writer.utils.color_utils import fmt_cn


class LabelId(ttk.Label):
    def __init__(self, parent, id_, *args, **kwargs):
        """Create a label with an id_ attached"""
        logg = logging.getLogger(f"c.{__class__.__name__}.__init__")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('__init__')}")

        self.id_ = id_
        super().__init__(parent, *args, **kwargs)

    def register_scroll_func(self, func):
        logg = logging.getLogger(f"c.{__class__.__name__}.register_scroll_func")
        #  logg.setLevel("TRACE")
        logg.log(5, f"{fmt_cn('Register')} scroll function")

        self.bind("<4>", func)
        self.bind("<5>", func)
        self.bind("<MouseWheel>", func)

    def on_enter(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_enter")
        #  logg.setLevel("TRACE")
        logg.log(5, f"{fmt_cn('Enter')} LabelId {self.id_}")
        logg.log(5, f"Event {event} fired by {event.widget}")
        id_ = event.widget.id_
        logg.log(5, f"event.widget.id_: {id_}")

        self.event_generate("<<sp_header_enter>>")
        self.set_state("active")

    def on_leave(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_leave")
        #  logg.setLevel("TRACE")
        logg.log(5, f"{fmt_cn('Leave')} LabelId {self.id_}")

        self.event_generate("<<sp_header_leave>>")
        self.set_state("!active")

    def on_button1_press(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_button1_press")
        #  logg.setLevel("TRACE")
        logg.debug(f"Clicked {fmt_cn('Button-1')} on LabelId {self.id_}")
        self.event_generate("<<sp_header_btn1_press>>")

    def set_state(self, the_state):
        """Sets the state of the label"""
        logg = logging.getLogger(f"c.{__class__.__name__}.set_state")
        #  logg.setLevel("TRACE")
        logg.log(5, f"Start {fmt_cn('set_state')} {the_state}")

        self.state([the_state])
