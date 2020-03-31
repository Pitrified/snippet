import argparse
import logging
from random import seed as rseed
from timeit import default_timer as timer

import tkinter as tk
from tkinter import ttk


class ExamplePackApp:
    def __init__(self):
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug(f"Starting __init__")

        self.root = tk.Tk()
        self.width = 900
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.title(f"Example of using ttk styles and pack geometry manager")

        self.pad = 10
        self.padx = self.pad
        self.pady = self.pad

        self.setup_style()

        self.toolbar = ttk.Frame(self.root, style="SToolbar.TFrame")
        self.toolbar.pack(
            side="top", anchor="n", fill="x", padx=self.padx, pady=self.pady,
        )

        self.maincontainer = ttk.Frame(self.root, style="SMain.TFrame")
        self.maincontainer.pack(
            side="top",
            anchor="n",
            fill="both",
            expand=True,
            padx=self.padx,
            pady=self.pady,
        )

        # we explicitly set the width
        self.sidebar = ttk.Frame(self.maincontainer, width=300, style="SSidebar.TFrame")
        self.sidebar.pack(
            side="left",
            anchor="w",
            fill="y",
            expand=False,
            padx=self.padx,
            pady=self.pady,
        )
        # and prevent childern element to influence the dimensions
        self.sidebar.pack_propagate(False)

        self.central_area = ttk.Frame(self.maincontainer, style="SCentral.TFrame")
        self.central_area.pack(
            side="left",
            anchor="w",
            fill="both",
            expand=True,
            padx=self.padx,
            pady=self.pady,
        )

        # put things in the toolbar
        # the toolbar frame will shrink to fit the content
        btn1 = ttk.Button(self.toolbar, text="Choice 1", style="Sbtn.TButton")
        btn2 = ttk.Button(self.toolbar, text="Choice 2", style="Sbtn.TButton")
        btn3 = ttk.Button(self.toolbar, text="Choice 3", style="Sbtn.TButton")
        btn1.pack(
            side="left", fill=None, expand=False, padx=self.padx, pady=self.pady,
        )
        btn2.pack(
            side="left", fill=None, expand=False, padx=self.padx, pady=self.pady,
        )
        btn3.pack(
            side="left", fill=None, expand=False, padx=self.padx, pady=self.pady,
        )

        self.title_lab1 = ttk.Label(self.sidebar, text="Info:", style="STitle.TLabel")
        self.title_lab1.pack(padx=self.padx, pady=self.pady)
        self.info_lab1 = ttk.Label(self.sidebar, text="Fill x", style="SInfo.TLabel")
        self.info_lab1.pack(padx=self.padx, pady=3, fill="x")
        self.info_lab2 = ttk.Label(self.sidebar, text="Anchor e", style="SInfo.TLabel")
        self.info_lab2.pack(padx=self.padx, pady=3, anchor="e")
        self.title_lab2 = ttk.Label(self.sidebar, text="Info:", style="STitle.TLabel")
        self.title_lab2.pack(padx=self.padx, pady=self.pady)
        self.info_lab3 = ttk.Label(self.sidebar, text="Fill x", style="SInfo.TLabel")
        self.info_lab3.pack(padx=self.padx, pady=3, fill="x")
        self.info_lab4 = ttk.Label(self.sidebar, text="Anchor e", style="SInfo.TLabel")
        self.info_lab4.pack(padx=self.padx, pady=3, anchor="e")

    def setup_style(self):
        logg = logging.getLogger(f"c.{__name__}.setup_style")
        logg.debug(f"Starting setup_style")

        toplevel = self.root.winfo_toplevel()
        logg.debug(f"self.root.winfo_toplevel(): {toplevel}")
        toplevel["background"] = "RoyalBlue1"

        s = ttk.Style()

        logg.debug(f"s.theme_names(): {s.theme_names()}")

        # configure root style
        s.configure(".", font=("Helvetica", 18))

        s.configure("TFrame", relief="sunken", borderwidth=5)
        s.configure("SToolbar.TFrame", background="bisque")
        s.configure("SMain.TFrame", background="aquamarine")
        s.configure("SSidebar.TFrame", background="pale turquoise")
        s.configure("SCentral.TFrame", background="forest green")

        s.configure("TButton", background="gold2", borderwidth=5)

        # sets dynamic values
        #  https://docs.python.org/3/library/tkinter.ttk.html#tkinter.ttk.Style.map
        s.map(
            "TButton",
            foreground=[("disabled", "yellow"), ("pressed", "red"), ("active", "blue")],
            background=[
                ("disabled", "magenta"),
                ("pressed", "!focus", "cyan"),
                ("active", "green"),
            ],
            highlightcolor=[("focus", "green"), ("!focus", "red")],
            relief=[("pressed", "groove"), ("!pressed", "ridge")],
        )

        s.configure(
            "STitle.TLabel",
            background="orange",
            padding=(60, 7, 60, 7),
            borderwidth=3,
            relief="groove",
        )
        s.configure(
            "SInfo.TLabel", background="steel blue", padding=(4, 1, 4, 1),
        )

        # inspect the layot of a button
        #  https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/ttk-layouts.html
        layout = s.layout("TButton")
        logg.debug(f"layout: {layout}")
        for element in ["highlight", "border", "focus", "padding", "label"]:
            el_op = s.element_options(f"Button.{element}")
            logg.debug(f"{element} options: {el_op}")

        logg.debug(
            f"s.lookup('Button.label', 'foreground'): {s.lookup('Button.label', 'foreground')}"
        )

    def run(self):
        self.root.mainloop()


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="hp.jpg",
        help="path to input image to use",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')

    # example log line
    logg = logging.getLogger(f"c.{__name__}.setup_logger")
    logg.debug(f"Done setting up logger")


def setup_env():
    setup_logger()

    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = f"python3 example_ttk_pack.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def run_example_ttk_pack(args):
    """
    """
    logg = logging.getLogger(f"c.{__name__}.run_example_ttk_pack")
    logg.debug(f"Starting run_example_ttk_pack")

    app = ExamplePackApp()
    app.run()


if __name__ == "__main__":
    args = setup_env()
    run_example_ttk_pack(args)
