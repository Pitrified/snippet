import logging

import tkinter as tk


class SidePanel(tk.Frame):
    def __init__(self, *args, **kwargs):
        log = logging.getLogger(f"c.{__name__}.init")
        log.debug('Start init')

        tk.Frame.__init__(self, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.plotBut = tk.Button(self, text="Plot ")
        self.plotBut.grid(row=0, column=0, sticky="ew")

        self.clearButton = tk.Button(self, text="Clear")
        self.clearButton.grid(row=1, column=0, sticky="ew")
