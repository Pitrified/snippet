import logging
import tkinter as tk
from tkinter import ttk


class ScrollableFrame(ttk.Frame):
    """A scrollable frame

    Thanks to the wizard BO https://stackoverflow.com/a/3092341
    """

    def __init__(self, parent, cv_bg, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # create scrollbar for canvas
        self.scroll_bar = ttk.Scrollbar(self, style="sf.Vertical.TScrollbar")

        # create the canvas and bind it to Scrollbar
        self.scroll_canvas = tk.Canvas(
            self,
            yscrollcommand=self.scroll_bar.set,
            background=cv_bg,
            highlightthickness=0,
        )

        # bind Scrollbar to Canvas
        self.scroll_bar.config(command=self.scroll_canvas.yview)

        # create the Frame to put inside the Canvas
        self.scroll_frame = ttk.Frame(self.scroll_canvas, style="sf.TFrame")

        # pack the canvas and the scrollbar in the ScrollableFrame
        #  self.scroll_bar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        # place the Frame on the Canvas
        self.scroll_canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw", tags="self.scroll_frame",
        )

        # bind resizing of canvas scrollregion
        self.scroll_frame.bind("<Configure>", self.on_scroll_frame_configure)

        # bind scroll to empty canvas (background outside frame)
        self.scroll_canvas.bind("<4>", self.on_list_scroll)
        self.scroll_canvas.bind("<5>", self.on_list_scroll)
        self.scroll_canvas.bind("<MouseWheel>", self.on_list_scroll)

    def on_scroll_frame_configure(self, event):
        """Reset the scroll region to encompass the inner frame"""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def on_list_scroll(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.on_list_scroll")
        if event.num == 4 or event.delta == 120 or event.delta == 1:
            number = -1
        elif event.num == 5 or event.delta == -120 or event.delta == -1:
            number = 1
        else:
            logg.error(f"Errors when scrolling {event}")

        logg.trace(f"Scrolling list {number} units, event {event} from {event.widget}")
        self.scroll_canvas.yview_scroll(number, "units")
