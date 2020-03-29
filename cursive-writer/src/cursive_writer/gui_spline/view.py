import logging
import tkinter as tk

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import collide_line_box
from cursive_writer.utils.geometric_utils import translate_point_dxy


class View:
    def __init__(self, root):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

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

    ### HELPERS ###

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

    ### REACTIONS TO OBSERVABLES ###

    def update_pf_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_pf_input_image")
        logg.info(f"{fmt_cn('Updating', 'start')} pf_input_image '{pf_input_image}'")
        # TODO write this name somewhere LOL


class FrameInfo(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for the frame
        #  self.grid_rowconfigure(0, weight=1)
        #  self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # frame for font measurement related buttons
        self.font_measurement_frame = tk.Frame(self, background="burlywood2")

        # setup grid for font_measurement_frame
        self.font_measurement_frame.grid_columnconfigure(0, weight=1)

        # build the objects in font_measurement_frame
        self.fm_title = tk.Label(
            self.font_measurement_frame,
            text="Font Measurement",
            background=self.font_measurement_frame.cget("background"),
        )

        self.fm_btn_set_base_mean = tk.Button(
            self.font_measurement_frame,
            text="Set base to mean dist",
            borderwidth=0,
            highlightthickness=0,
            background="wheat2",
            activebackground="wheat1",
        )

        self.fm_btn_set_base_ascent = tk.Button(
            self.font_measurement_frame,
            text="Set base to ascent dist",
            borderwidth=0,
            highlightthickness=0,
            background="wheat2",
            activebackground="wheat1",
        )

        # grid the objects in font_measurement_frame
        self.fm_title.grid(row=0, column=0, sticky="ew")
        self.fm_btn_set_base_mean.grid(row=1, column=0, sticky="ew")
        self.fm_btn_set_base_ascent.grid(row=2, column=0, sticky="ew")

        # frame for mouse pos / line orientation informations
        self.mouse_info_frame = tk.Frame(self, background="burlywood2")

        # setup grid for mouse_info_frame
        self.mouse_info_frame.grid_columnconfigure(0, weight=1)

        # mouse_info_frame title label
        self.mi_title = tk.Label(
            self.mouse_info_frame,
            text="Mouse info",
            background=self.font_measurement_frame.cget("background"),
        )

        # create mouse pos info label
        self.mi_var_pos = tk.StringVar(self.mouse_info_frame)
        self.mi_label_pos = tk.Label(
            self.mouse_info_frame,
            textvariable=self.mi_var_pos,
            background=self.cget("background"),
        )
        self.mi_var_pos.set("Mouse at (0, 0)")

        # grid mouse_info_frame elements
        self.mi_title.grid(row=0, column=0, sticky="ew")
        self.mi_label_pos.grid(row=1, column=0, sticky="ew")

        # grid the frames
        self.font_measurement_frame.grid(row=0, column=0, sticky="ew")
        self.mouse_info_frame.grid(row=1, column=0, sticky="ew")

    ### REACTIONS TO OBSERVABLES ###

    def update_curr_mouse_pos(self, pos):
        logg = logging.getLogger(f"c.{__name__}.update_curr_mouse_pos")
        logg.setLevel("INFO")
        pos_str = f"Mouse at ({pos[0]}, {pos[1]})"
        logg.debug(f"{fmt_cn('Start', 'start')} update_curr_mouse_pos - {pos_str}")
        self.mi_var_pos.set(pos_str)


class FrameImage(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

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

    ### REACTIONS TO OBSERVABLES ###

    def update_crop_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_crop_input_image")
        #  logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Start', 'start')} update_crop_input_image")

        image = data["image_res"]
        self.widget_shift_x = data["widget_shift_x"]
        self.widget_shift_y = data["widget_shift_y"]
        self.resized_wid = data["resized_wid"]
        self.resized_hei = data["resized_hei"]

        # delete the old image in the canvas
        self.image_canvas.delete("image")
        # draw the new one
        self.image_canvas.create_image(
            self.widget_shift_x,
            self.widget_shift_y,
            image=image,
            anchor="nw",
            tags="image",
        )

        # get bbox of the image in the canvas
        # MAYBE save this when putting the image on the canvas...
        left = self.widget_shift_x
        top = self.widget_shift_y
        right = left + self.resized_wid
        bot = top + self.resized_hei
        logg.debug(f"left: {left} top: {top} right: {right} bot: {bot}")
        self.image_bbox = (left, top, right, bot)

    def update_free_line(self, line_point):
        """
        """
        logg = logging.getLogger(f"c.{__name__}.update_free_line")
        logg.debug(f"{fmt_cn('Start', 'start')} update_free_line {line_point}")

        if line_point is None:
            self.image_canvas.delete("free_line")
            return

        self.draw_line(line_point, tag="free_line", fill="red")

    def update_fm_lines(self, fm_lines):
        """
        """
        logg = logging.getLogger(f"c.{__name__}.update_fm_lines")
        logg.debug(f"{fmt_cn('Start', 'start')} update_fm_lines {fm_lines}")

        self.draw_line(
            fm_lines["vert_point"], tag="vert_point", dash=(6, 6), fill="red"
        )
        self.draw_line(fm_lines["base_point"], tag="base_point", fill="red")
        self.draw_line(fm_lines["mean_point"], tag="mean_point", fill="red")
        self.draw_line(fm_lines["ascent_point"], tag="ascent_point", fill="red")
        self.draw_line(fm_lines["descent_point"], tag="descent_point", fill="red")

    def update_click_start_pos(self, start_pos):
        """
        """
        logg = logging.getLogger(f"c.{__name__}.update_click_start_pos")
        logg.debug(f"{fmt_cn('Start', 'start')} update_click_start_pos {start_pos}")

        # if the Observable has been emptied remove the circle
        if start_pos is None:
            self.image_canvas.delete("click_start_pos")
            return

        # translate the point from image to canvas
        canv_point_x = start_pos[0] + self.widget_shift_x
        canv_point_y = start_pos[1] + self.widget_shift_y
        circ_dim = 2
        # get the circle dimension
        circ_bbox = (
            canv_point_x - circ_dim,
            canv_point_y - circ_dim,
            canv_point_x + circ_dim,
            canv_point_y + circ_dim,
        )
        logg.debug(f"circ_bbox: {circ_bbox}")
        self.image_canvas.create_oval(
            *circ_bbox, tag="click_start_pos", fill="red", width=1
        )

    ### HELPERS ###

    def draw_line(self, image_point, tag, **kwargs):
        """Add a line on the point
        """
        logg = logging.getLogger(f"c.{__name__}.draw_line")
        logg.debug(f"{fmt_cn('Start', 'start')} draw_line")

        # the line_point are in the image coordinate
        # shift them to canvas coordinate
        #  line_point.translate(self.widget_shift_x, self.widget_shift_y)
        canv_point = translate_point_dxy(
            image_point, self.widget_shift_x, self.widget_shift_y
        )

        # compute the intersections
        admissible_inter = collide_line_box(self.image_bbox, canv_point)

        if len(admissible_inter) == 0:
            logg.debug(f"No line found inside the image")
            return
        elif len(admissible_inter) != 2:
            logg.debug(f"Weird amount of intersections found {len(admissible_inter)}")
            return

        # delete the old free_line in the canvas
        self.image_canvas.delete(tag)

        x0 = admissible_inter[0][0]
        y0 = admissible_inter[0][1]
        x1 = admissible_inter[1][0]
        y1 = admissible_inter[1][1]
        self.image_canvas.create_line(x0, y0, x1, y1, tags=tag, **kwargs)

    def bind_canvas(self, kind, func):
        """Bind event 'kind' to func *only* on image_canvas
        """
        self.image_canvas.bind(kind, func)


class FrameSpline(tk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Start', 'start')} init")

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
