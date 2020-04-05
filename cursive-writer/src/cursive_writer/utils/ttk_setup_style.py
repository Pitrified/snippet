import logging
import tkinter as tk
from tkinter import ttk
from cursive_writer.utils.color_utils import fmt_cn


def setup_style():
    logg = logging.getLogger(f"c.{__name__}.setup_style")
    #  logg.setLevel("TRACE")
    logg.info(f"Start {fmt_cn('init', 'setup_style')}")

    s = ttk.Style()

    the_font = "Helvetica"

    # configure root style
    s.configure(".", font=(the_font, 12))

    ### FRAMES ###

    s.configure("container.TFrame", background="burlywood1")
    s.configure("group.TFrame", background="burlywood2")

    # ScrollableFrame
    s.configure("sf.TFrame", background="burlywood2")
    s.configure(
        "sf.Vertical.TScrollbar",
        background="red",
        borderwidth=0,
        troughcolor="blue",
        highlightthickness=0,
    )
    s.map(
        "sf.Vertical.TScrollbar",
        background=[("active", "green"), ("pressed", "yellow"),],
    )

    ### LABELS ###

    s.configure("TLabel", anchor=tk.CENTER)
    s.configure(
        "title.TLabel",
        background="burlywood3",
        font=(the_font, 14),
        padding=(0, 6, 0, 6),
    )
    s.configure("info.TLabel", background="burlywood2")

    s.configure(
        "sp_info.TLabel",
        background="burlywood2",
        anchor=tk.CENTER,
        #  font=("Courier", 12),
        #  font=("Consolas", 10),
    )
    s.map(
        "sp_info.TLabel", background=[("selected", "tan2"), ("active", "wheat1"),],
    )
    s.configure(
        "sp_pos.sp_info.TLabel", font=("Consolas", 10),
    )
    s.configure(
        "sp_header.sp_info.TLabel", font=("Consolas", 12), padding=(0, 3, 0, 3),
    )

    ### ENTRY ###

    s.configure(
        "root.TEntry",
        background="wheat2",
        borderwidth=0,
        highlightthickness=0,
        fieldbackground="wheat1",
    )

    ### BUTTONS ###

    s.configure(
        "settings.TButton", background="wheat2", borderwidth=0, highlightthickness=0,
    )
    s.map(
        "settings.TButton",
        background=[("pressed", "wheat1"), ("active", "wheat1"),],
        highlightbackground=[("pressed", "red")],
        highlightcolor=[("pressed", "red")],
    )
    logg.debug(f"s.layout('settings.TButton'): {s.layout('settings.TButton')}")
    # original layout
    #  s.layout('settings.TButton', [('Button.border', {'sticky': 'nswe',
    #  'border': '1', 'children': [('Button.focus', {'sticky': 'nswe',
    #  'children': [('Button.padding', {'sticky': 'nswe', 'children':
    #  [('Button.label', {'sticky': 'nswe'})]})]})]})])
    s.layout(
        "settings.TButton",
        [
            (
                "Button.border",
                {
                    "sticky": "nswe",
                    "border": "1",
                    "children": [
                        (
                            "Button.padding",
                            {
                                "sticky": "nswe",
                                "children": [("Button.label", {"sticky": "nswe"})],
                            },
                        )
                    ],
                },
            )
        ],
    )
