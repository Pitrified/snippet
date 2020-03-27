import logging
import tkinter as tk


class View:
    def __init__(self, root):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info("Start init")

        self.root = root

        self.frame_info = FrameInfo(
            self.root, name="frame_info", background="burlywood1"
        )
        self.frame_image = FrameImage(
            self.root, name="frame_image", background="burlywood2"
        )
        self.frame_spline = FrameSpline(
            self.root, name="frame_spline", background="burlywood1"
        )

        self.setup_main_window()

        self.setup_layout()

    def setup_main_window(self):
        """Setup main window aesthetics
        """
        self.width = 900
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")

    def setup_layout(self):
        # row 0 expands
        self.root.grid_rowconfigure(0, weight=1)
        # column 1 expands
        self.root.grid_columnconfigure(1, weight=1)

        self.frame_info.grid(row=0, column=0, sticky="ns")
        self.frame_image.grid(row=0, column=1, sticky="nsew")
        self.frame_spline.grid(row=0, column=2, sticky="ns")

    def exit(self):
        # TODO ask confirmation
        self.root.destroy()

    def update_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_input_image")
        logg.info(f"Updating pf_input_image '{pf_input_image}'")


class FrameImage(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start init")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_label = tk.Label(
            self, text="Mock up FrameImage", bg=self.cget("background")
        )

        #  # grid it, do not expand
        #  self.image_label.grid(row=0, column=0)

        #  # create the canvas, size in pixels
        #  self.canvas = Canvas(width=300, height=200, bg="black")

        #  # pack the canvas into a frame/form
        #  canvas.pack(expand=YES, fill=BOTH)

        #  # load the .gif image file
        #  gif1 = PhotoImage(file='small_globe.gif')

        #  # put gif image on canvas
        #  # pic's upper left corner (NW) on the canvas is at x=50 y=10
        #  canvas.create_image(50, 10, image=gif1, anchor=NW)


class FrameSpline(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start init")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.image_label = tk.Label(
            self, text="Mock up FrameSpline", background=self.cget("background")
        )

        # grid it, do not expand
        self.image_label.grid(row=0, column=0)


class FrameInfo(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start init")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create mockup label
        self.image_label = tk.Label(
            self, text="Mock up FrameInfo", background=self.cget("background")
        )

        # grid it, do not expand
        self.image_label.grid(row=0, column=0)
