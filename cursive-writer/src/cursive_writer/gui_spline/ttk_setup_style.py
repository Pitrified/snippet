import logging
import platform
import tkinter as tk
from tkinter import ttk
from cursive_writer.utils.color_utils import fmt_cn

# color list
# https://stackoverflow.com/a/12434606/2237151
# http://www.tcl.tk/man/tcl8.5/TkCmd/colors.htm


def _from_rgb(r, g, b):
    """Translates rgb values to a tkinter friendly color code (#F0F8FF)
    """
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def setup_style(colorscheme="terra"):
    logg = logging.getLogger(f"c.{__name__}.setup_style")
    #  logg.setLevel("TRACE")
    logg.info(f"Start {fmt_cn('init', 'setup_style')}")

    # option dict
    o = {}

    if colorscheme.startswith("terra"):
        # frames
        o["bg_general"] = "burlywood1"
        o["bg_container"] = "burlywood2"
        o["bg_title"] = "burlywood3"
        # button background
        o["bg_btn"] = "wheat2"
        # hovered element
        o["bg_active"] = "wheat1"
        # selected element select accent color
        if "tan" in colorscheme:
            o["bg_selected"] = "tan2"
        # default accent for terra colorscheme
        else:
            o["bg_selected"] = "olive drab"
        # text color of title frames
        o["fg_title"] = "gray7"

    elif colorscheme.startswith("slategray"):
        # frames
        o["bg_general"] = "light slate gray"
        o["bg_container"] = "slate gray"
        # o["bg_title"] = "dark slate gray" # 47 79 79
        o["bg_title"] = _from_rgb(47 + 30, 79 + 30, 79 + 40)
        # button background
        # o["bg_btn"] = "azure4" # 131 139 139
        o["bg_btn"] = _from_rgb(131 + 30, 139 + 30, 139 + 40)
        # hovered element
        o["bg_active"] = "light gray"
        # selected element
        o["bg_selected"] = "coral3"
        o["fg_title"] = "white smoke"

    # default colorscheme == "snow":
    else:
        # frames
        o["bg_general"] = "snow2"
        o["bg_container"] = "snow3"
        o["bg_title"] = "snow4"
        # button background
        o["bg_btn"] = "snow"
        # hovered element
        o["bg_active"] = "mint cream"
        # selected element
        o["bg_selected"] = "coral"
        o["fg_title"] = "white"

    # get the rgb values of the container color, needed for plot bg
    rgb = tk.Button().winfo_rgb(o["bg_container"])
    o["bg_container_rgb"] = tuple(c / 65535 for c in rgb)
    logg.trace(f"o['bg_container_rgb']: {o['bg_container_rgb']}")

    # font setup
    o["font_std_type"] = "Helvetica"
    o["font_mono_type"] = "Consolas"

    sys_type = platform.system()
    uname_version = platform.uname().version
    logg.info(f"sys_type: {sys_type} uname_version: {uname_version}")

    # check if we are in WSL
    if "Microsoft" in uname_version:
        o["font_std_size"] = 12
        o["font_mono_size"] = 10

    # or regular Linux
    elif sys_type == "Linux":
        o["font_std_size"] = 9
        o["font_mono_size"] = 8

    # or somewhere else, I guess
    else:
        o["font_std_size"] = 12
        o["font_mono_size"] = 10

    s = ttk.Style()

    # configure root style
    s.configure(".", font=(o["font_std_type"], o["font_std_size"]))

    ### FRAMES ###

    s.configure("container.TFrame", background=o["bg_general"])
    s.configure("group.TFrame", background=o["bg_container"])

    # ScrollableFrame
    s.configure("sf.TFrame", background=o["bg_container"])

    ### LABELS ###

    s.configure("TLabel", anchor=tk.CENTER)
    s.configure(
        "title.TLabel",
        background=o["bg_title"],
        foreground=o["fg_title"],
        font=(o["font_std_type"], o["font_std_size"] + 2),
        padding=(0, 6, 0, 6),
    )
    s.configure("info.TLabel", background=o["bg_container"])

    s.configure(
        "sp_info.TLabel",
        background=o["bg_container"],
        anchor=tk.CENTER,
        #  font=("Courier", 12),
        #  font=("Consolas", 10),
    )
    s.map(
        "sp_info.TLabel",
        background=[("selected", o["bg_selected"]), ("active", o["bg_active"])],
    )
    s.configure(
        "sp_header.sp_info.TLabel",
        font=("Consolas", o["font_mono_size"] + 2),
        padding=(0, 3, 0, 3),
    )
    s.configure(
        "sp_pos.sp_info.TLabel", font=("Consolas", o["font_mono_size"]),
    )

    ### ENTRY ###

    s.configure(
        "root.TEntry",
        background=o["bg_btn"],
        borderwidth=0,
        highlightthickness=0,
        fieldbackground=o["bg_btn"],
    )

    ### BUTTONS ###

    s.configure(
        "settings.TButton", background=o["bg_btn"], borderwidth=0, highlightthickness=0,
    )
    s.map(
        "settings.TButton",
        background=[("pressed", o["bg_selected"]), ("active", o["bg_active"])],
        highlightbackground=[("pressed", "red")],
        highlightcolor=[("pressed", "red")],
    )
    logg.debug(f"s.layout('settings.TButton'): {s.layout('settings.TButton')}")
    # original layout
    #  s.layout('settings.TButton', [('Button.border', {'sticky': 'nswe',
    #  'border': '1', 'children': [('Button.focus', {'sticky': 'nswe',
    #  'children': [('Button.padding', {'sticky': 'nswe', 'children':
    #  [('Button.label', {'sticky': 'nswe'})]})]})]})])
    # remove the focus element to avoid dotted gray line
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

    return o
