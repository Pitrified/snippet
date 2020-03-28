import logging
import tkinter as tk


class View:
    def __init__(self, root):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info("Start init")

        self.root = root

        self.frame_info = FrameInfo(
            self.root, name="frame_info", background="burlywood1",
        )
        self.frame_image = FrameImage(
            self.root, name="frame_image", background="burlywood1"
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
        # column 0 does not expand but has min width
        #  self.root.grid_columnconfigure(0, weight=0)
        # column 1 expands
        self.root.grid_columnconfigure(1, weight=1)

        self.frame_info.grid(row=0, column=0, sticky="ns")
        self.frame_image.grid(row=0, column=1, sticky="nsew")
        self.frame_spline.grid(row=0, column=2, sticky="ns")

    def exit(self):
        # TODO ask confirmation
        self.root.destroy()

    def update_pf_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_pf_input_image")
        logg.info(f"Updating pf_input_image '{pf_input_image}'")
        # TODO write this name somewhere LOL


class FrameInfo(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start init")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for the frame
        #  self.grid_rowconfigure(0, weight=1)
        #  self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # frame for font measurement related buttons
        self.fm_frame = tk.Frame(self, background="burlywood2")

        # setup grid for fm_frame
        self.fm_frame.grid_columnconfigure(0, weight=1)

        # build the objects in fm_frame
        self.fm_title = tk.Label(
            self.fm_frame,
            text="Font Measurement",
            background=self.fm_frame.cget("background"),
        )

        self.fm_btn_set_base_mean = tk.Button(
            self.fm_frame,
            text="Set base to mean dist",
            borderwidth=0,
            highlightthickness=0,
            background="wheat2",
            activebackground="wheat1",
        )

        self.fm_btn_set_base_ascent = tk.Button(
            self.fm_frame,
            text="Set base to ascent dist",
            borderwidth=0,
            highlightthickness=0,
            background="wheat2",
            activebackground="wheat1",
        )

        # grid the objects in fm_frame
        self.fm_title.grid(row=0, column=0, sticky="ew")
        self.fm_btn_set_base_mean.grid(row=1, column=0, sticky="ew")
        self.fm_btn_set_base_ascent.grid(row=2, column=0, sticky="ew")

        # frame for mouse pos / line orientation informations
        self.mouse_info_frame = tk.Frame(self)

        # create mockup label
        self.tmp_label = tk.Label(
            self.mouse_info_frame,
            text="Mock up mouse_info_frame",
            background=self.cget("background"),
        )

        # grid it
        self.tmp_label.grid(row=0, column=0, sticky="ew")

        # grid the frames
        self.fm_frame.grid(row=0, column=0, sticky="ew")
        self.mouse_info_frame.grid(row=1, column=0, sticky="ew")


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

        #  # mockup label to draw the frame
        #  self.image_label = tk.Label( self, text="Mock up FrameImage", bg=self.cget("background"))
        #  # grid it, do not expand
        #  self.image_label.grid(row=0, column=0)

        # create the canvas, size in pixels, width=300, height=200
        # the size is not needed, because is gridded with sticky option
        self.image_canvas = tk.Canvas(self, bg="black")

        # pack the canvas into a frame/form
        self.image_canvas.grid(row=0, column=0, sticky="nsew")

    def update_crop_input_image(self, data):
        image = data["image_res"]
        x = data["widget_shift_x"]
        y = data["widget_shift_y"]
        # delete the old image in the canvas
        self.image_canvas.delete("image")
        # draw the new one
        self.image_canvas.create_image(x, y, image=image, anchor="nw", tags="image")

    def bind_canvas(self, kind, func):
        """Bind event 'kind' to func *only* on image_canvas
        """
        self.image_canvas.bind(kind, func)


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
