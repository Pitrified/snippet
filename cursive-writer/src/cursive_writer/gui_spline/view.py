import logging
import tkinter as tk
from tkinter import ttk

from math import cos
from math import sin

from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import collide_line_box
from cursive_writer.utils.geometric_utils import translate_point_dxy
from cursive_writer.gui_spline.spoint_frame import FrameSPoint
from cursive_writer.gui_spline.scrollable_frame import ScrollableFrame


class View:
    def __init__(self, root):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        self.root = root

        self.sidebar_width = 250

        self.frame_info = FrameInfo(
            self.root,
            name="frame_info",
            style="container.TFrame",
            width=self.sidebar_width,
        )
        self.frame_image = FrameImage(
            self.root, name="frame_image", style="container.TFrame"
        )
        self.frame_spline = FrameSpline(
            self.root,
            name="frame_spline",
            style="container.TFrame",
            width=self.sidebar_width,
        )

        self.setup_main_window()

        self.setup_layout()

        self.setup_style()

    ### HELPERS ###

    def setup_main_window(self):
        """Setup main window aesthetics
        """
        self.width = 900
        self.height = 600
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.title(f"Spline builder GUI")

    def setup_layout(self):
        # row 0 expands
        self.root.grid_rowconfigure(0, weight=1)
        # column 1 expands
        self.root.grid_columnconfigure(1, weight=1)

        self.frame_info.grid(row=0, column=0, sticky="ns")
        # DO NOT let children widget influence the frame dimension
        self.frame_info.grid_propagate(False)
        self.frame_image.grid(row=0, column=1, sticky="nsew")
        self.frame_spline.grid(row=0, column=2, sticky="ns")
        self.frame_spline.grid_propagate(False)

    def setup_style(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.setup_style")
        logg.setLevel("TRACE")
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
            "sp_pos.TLabel",
            background="burlywood2",
            anchor=tk.CENTER,
            font=("Courier", 12),
        )
        s.map(
            "sp_pos.TLabel", background=[("selected", "tan2"), ("active", "wheat1"),],
        )

        ### BUTTONS ###

        s.configure(
            "settings.TButton",
            background="wheat2",
            borderwidth=0,
            highlightthickness=0,
        )
        s.map(
            "settings.TButton",
            background=[("pressed", "wheat1"), ("active", "wheat1"),],
        )

    def reset_focus(self):
        """
        """
        self.root.focus_set()

    def exit(self):
        # TODO ask confirmation
        self.root.destroy()

    ### REACTIONS TO OBSERVABLES ###

    def update_pf_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_pf_input_image")
        logg.info(f"{fmt_cn('Updating', 'start')} pf_input_image '{pf_input_image}'")
        # TODO write this name somewhere LOL

    def update_visible_SP(self, data):
        """Update the drawn arrows

        MAYBE change background of the visible SP?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_visible_SP")
        logg.debug(f"Start {fmt_cn('update_visible_SP', 'start')}")

        self.frame_image.do_update_visible_SP(data)


class FrameInfo(ttk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # frame for font measurement related buttons
        self.font_measurement_frame = ttk.Frame(self, style="group.TFrame")

        # setup grid for font_measurement_frame
        self.font_measurement_frame.grid_columnconfigure(0, weight=1)
        self.font_measurement_frame.grid_columnconfigure(1, weight=1)

        # build the objects in font_measurement_frame
        self.fm_title = ttk.Label(
            self.font_measurement_frame, text="Font Measurement", style="title.TLabel"
        )

        self.fm_btn_set_base_mean = ttk.Button(
            self.font_measurement_frame, text="Set BM", style="settings.TButton",
        )

        self.fm_btn_set_base_ascent = ttk.Button(
            self.font_measurement_frame, text="Set BA", style="settings.TButton",
        )

        # grid the objects in font_measurement_frame
        self.fm_title.grid(row=0, column=0, sticky="ew", columnspan=2)
        #  self.fm_btn_set_base_mean.grid(row=1, column=0, sticky="ew")
        #  self.fm_btn_set_base_ascent.grid(row=2, column=0, sticky="ew")
        self.fm_btn_set_base_mean.grid(row=1, column=0, pady=4)
        self.fm_btn_set_base_ascent.grid(row=1, column=1, pady=4)

        # frame for mouse pos / line orientation informations
        self.mouse_info_frame = ttk.Frame(self, style="group.TFrame")

        # setup grid for mouse_info_frame
        self.mouse_info_frame.grid_columnconfigure(0, weight=1)

        # mouse_info_frame title label
        self.mi_title = ttk.Label(
            self.mouse_info_frame, text="Mouse info", style="title.TLabel"
        )

        # create mouse pos info label
        self.mi_var_pos = tk.StringVar(self.mouse_info_frame)
        self.mi_label_pos = ttk.Label(
            self.mouse_info_frame, textvariable=self.mi_var_pos, style="info.TLabel",
        )
        self.mi_var_pos.set("Mouse at (0, 0)")

        # create state info label
        self.mi_var_state = tk.StringVar(self.mouse_info_frame)
        self.mi_label_state = ttk.Label(
            self.mouse_info_frame, textvariable=self.mi_var_state, style="info.TLabel",
        )
        self.mi_var_state.set("State: FREE")

        # grid mouse_info_frame elements
        self.mi_title.grid(row=0, column=0, sticky="ew")
        self.mi_label_pos.grid(row=1, column=0, sticky="ew")
        self.mi_label_state.grid(row=2, column=0, sticky="ew")

        # grid the frames
        self.font_measurement_frame.grid(
            row=0, column=0, sticky="new", padx=10, pady=10
        )
        self.mouse_info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

    ### REACTIONS TO OBSERVABLES ###

    def update_curr_mouse_pos(self, pos):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_curr_mouse_pos")
        logg.setLevel("INFO")
        pos_str = f"Mouse at ({pos[0]}, {pos[1]})"
        logg.debug(f"Start {fmt_cn('update_curr_mouse_pos', 'start')} - {pos_str}")
        self.mi_var_pos.set(pos_str)

    def update_state(self, state):
        """Update the label with the current state
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_state")
        logg.debug(f"Start {fmt_cn('update_state', 'start')} {state}")
        if state == "free":
            state_str = f"State: FREE"
        elif state == "free_clicked_left":
            state_str = f"State: FREE_CLICK_L"
        elif state == "free_clicked_right":
            state_str = f"State: FREE_CLICK_R"
        elif state == "setting_base_mean":
            state_str = f"State: SET_BM"
        elif state == "setting_base_mean_clicked":
            state_str = f"State: SET_BM_CLICK"
        else:
            logg.error(f"{fmt_cn('Unrecognized', 'error')} system state {state}")
            return
        self.mi_var_state.set(state_str)


class FrameImage(ttk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the canvas, size in pixels, width=300, height=200
        # the size is not needed, because is gridded with sticky option
        self.image_canvas = tk.Canvas(self, bg="black", highlightthickness=0)

        # pack the canvas into a frame/form
        self.image_canvas.grid(row=0, column=0, sticky="nsew")

    ### REACTIONS TO OBSERVABLES ###

    def update_crop_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_crop_input_image")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('update_crop_input_image', 'start')}")

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
        logg = logging.getLogger(f"c.{__class__.__name__}.update_free_line")
        logg.debug(f"Start {fmt_cn('update_free_line', 'start')} {line_point}")

        if line_point is None:
            self.image_canvas.delete("free_line")
            return

        self.draw_line(line_point, tag="free_line", fill="red")

    def update_fm_lines(self, fm_lines):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_fm_lines")
        logg.debug(f"Start {fmt_cn('update_fm_lines', 'start')} {fm_lines}")

        self.draw_line(
            fm_lines["vert_point"], tag="vert_point", dash=(6, 6), fill="red"
        )
        self.draw_line(fm_lines["base_point"], tag="base_point", fill="red")
        self.draw_line(fm_lines["mean_point"], tag="mean_point", fill="red")
        self.draw_line(fm_lines["ascent_point"], tag="ascent_point", fill="red")
        self.draw_line(fm_lines["descent_point"], tag="descent_point", fill="red")

    def update_click_left_start_pos(self, start_pos):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_click_left_start_pos")
        logg.debug(
            f"Start {fmt_cn('update_click_left_start_pos', 'start')} {start_pos}"
        )

        # if the Observable has been emptied remove the circle
        if start_pos is None:
            self.image_canvas.delete("click_left_start_pos")
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
            *circ_bbox, tag="click_left_start_pos", fill="red", width=1
        )

    ### HELPERS ###

    def do_update_visible_SP(self, data):
        """Update the drawn arrows
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.do_update_visible_SP")
        logg.debug(f"Start {fmt_cn('do_update_visible_SP', 'start')}")

        self.image_canvas.delete("spline_point")

        for spid in data:
            self.draw_point(data[spid], "spline_point")

    def draw_point(self, view_op, tag, length=-1):
        """Draw a point on the canvas
        """
        if length == -1:
            min_dim = min(self.resized_wid, self.resized_hei)
            length = min_dim * 0.10

        canv_x = view_op.x + self.widget_shift_x
        canv_y = view_op.y + self.widget_shift_y
        end_x = canv_x + length * cos(view_op.ori_rad)
        end_y = canv_y + length * sin(view_op.ori_rad)
        self.image_canvas.create_line(
            canv_x, canv_y, end_x, end_y, tags=tag, arrow=tk.LAST, fill="cyan"
        )

    def draw_line(self, image_point, tag, **kwargs):
        """Add a line on the point
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.draw_line")
        logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('draw_line', 'start')}")

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


class FrameSpline(ttk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        self.all_SP_frames = {}
        self.old_selected = 0

        ########################
        ### SETUP this frame ###
        ########################

        # setup grid for the frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the child frames
        self.spline_header_frame = ttk.Frame(self, style="group.TFrame")
        self.spline_list_frame = ttk.Frame(self, style="group.TFrame")
        # grid the frames
        self.spline_header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        self.spline_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        ###############################################
        ### SETUP frame for spline buttons and info ###
        ###############################################

        # setup grid for spline_header_frame
        self.spline_header_frame.grid_columnconfigure(0, weight=1)

        # create the elements
        self.sh_title = ttk.Label(
            self.spline_header_frame, text="Title INFO", style="title.TLabel"
        )
        self.sh_btn_new_spline = ttk.Button(
            self.spline_header_frame, text="New spline", style="settings.TButton",
        )

        # grid the elements in spline_header_frame
        self.sh_title.grid(row=0, column=0, sticky="ew")
        self.sh_btn_new_spline.grid(row=1, column=0, pady=4)

        #####################################
        ### SETUP frame for spline points ###
        #####################################

        # setup grid for spline_list_frame
        self.spline_list_frame.grid_rowconfigure(1, weight=1)
        self.spline_list_frame.grid_columnconfigure(0, weight=1)

        # header for this frame
        self.sl_title = ttk.Label(
            self.spline_list_frame, text="Title SPlist", style="title.TLabel"
        )
        # create the ScrollableFrame
        #  cv_bg = "blue"
        cv_bg = "burlywood2"
        self.sl_scrollable = ScrollableFrame(
            self.spline_list_frame, style="sf.TFrame", cv_bg=cv_bg
        )

        # grid the elements in spline_list_frame
        self.sl_title.grid(row=0, column=0, sticky="ew")
        self.sl_scrollable.grid(row=1, column=0, sticky="nsew")

        # create a fake label to force the scroll_frame to be wide
        # this is shady as hell
        # should be (frame_spline - 2*padx)
        sp_frames_width = 230
        sp_frames_height = 0
        self.sl_mock = ttk.Frame(
            self.sl_scrollable.scroll_frame, width=sp_frames_width, style="sf.TFrame",
        )
        self.sl_mock.grid(row=0, column=0)

    ### REACTIONS TO OBSERVABLES ###

    def update_all_SP(self, data):
        """Create a frame for each SP received
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_all_SP")
        logg.debug(f"Start {fmt_cn('update_all_SP', 'start')}")

        sp_frames_width = 220
        sp_frames_height = 50

        for spid in data:
            if not spid in self.all_SP_frames:
                name = f"frame_sp_{spid}"

                # create the sp_frame inside the ScrollableFrame
                # MAYBE this should have style set? The frame is completely
                # filled anyway by the element inside, so it doesn't show much
                sp_frame = FrameSPoint(
                    self.sl_scrollable.scroll_frame, name, data[spid],
                )

                # bind the mouse scroll on the FrameSPoint
                sp_frame.register_scroll_func(self.sl_scrollable.on_list_scroll)

                # bind events to the frame
                sp_frame.bind("<Enter>", sp_frame.on_enter)
                sp_frame.bind("<Leave>", sp_frame.on_leave)
                sp_frame.register_on_content("<Button-1>", sp_frame.on_button1_press)

                # save the frame
                self.all_SP_frames[spid] = sp_frame

    def do_update_visible_SP(self, data):
        """MAYBE change background of the visible SP?

        This is never called
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.do_update_visible_SP")
        logg.debug(f"Start {fmt_cn('do_update_visible_SP', 'start')}")

    def update_active_SP(self, data):
        """Grid the frames relative to the active SplinePoints
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_active_SP")
        logg.debug(f"Start {fmt_cn('update_active_SP', 'start')} {data}")

        # remove all frames from grid
        for spid, sp_frame in self.all_SP_frames.items():
            sp_frame.grid_forget()

        row = 0
        for glyph in data:
            for spid in glyph:
                self.all_SP_frames[spid].grid(row=row, column=0, sticky="ew")
                #  self.all_SP_frames[spid].grid(row=row, column=0, sticky="nsew")
                row += 1

    def update_selected_spid_SP(self, data):
        """TODO: what are you changing when updating selected_spid_SP?

            - selected: the widget is selected
            - active: the mouse is inside
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_selected_spid_SP")
        logg.debug(f"Start {fmt_cn('update_selected_spid_SP', 'start')} {data}")

        # clear old selected state
        self.all_SP_frames[self.old_selected].set_state("!selected")
        self.old_selected = data

        # set new one
        self.all_SP_frames[data].set_state("selected")

    ### HELPERS ###
