import logging

import tkinter as tk
from tkinter import ttk


class SidePanel(tk.Frame):
    def __init__(self, *args, **kwargs):
        log = logging.getLogger(f"c.{__name__}.init")
        log.info("Start init")

        tk.Frame.__init__(self, *args, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.funcList = ["cos", "sin"]
        self.selectedFunc = tk.StringVar(self)
        self.selectedFunc.set(self.funcList[0])

        # OptionMenu has to be tracked with StringVar.trace
        #  self.funcOpt = tk.OptionMenu(self, self.selectedFunc, *self.funcList)
        #  self.funcOpt.grid(row=0, column=0, sticky="ew")

        # Combobox has virtual event
        self.funcOpt = ttk.Combobox(
            self, textvariable=self.selectedFunc, values=self.funcList, state="readonly"
        )
        self.funcOpt.grid(row=0, column=0, sticky="ew")

        self.scaleX = tk.Scale(self, from_=0, to=4, orient=tk.HORIZONTAL)
        self.scaleX.set(1)
        self.scaleX.grid(row=1, column=0, sticky="ew")

        self.scaleY = tk.Scale(self, from_=0, to=4, orient=tk.HORIZONTAL)
        self.scaleY.set(1)
        self.scaleY.grid(row=2, column=0, sticky="ew")

        # this does nothing useful, it's here as an example
        self.plotBut = tk.Button(self, text="Plot ")
        self.plotBut.grid(row=3, column=0, sticky="ew")
