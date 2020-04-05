import logging
import tkinter as tk
from tkinter import ttk

from math import cos
from math import sin

from cursive_writer.gui_spline.spoint_frame import FrameSPoint
from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn
from cursive_writer.utils.geometric_utils import collide_line_box
from cursive_writer.utils.geometric_utils import translate_point_dxy
from cursive_writer.utils.scrollable_frame import ScrollableFrame
from cursive_writer.utils.ttk_setup_style import setup_style
from cursive_writer.utils.label_id import LabelId


class View:
    def __init__(self, root, sidebar_width=250, width=900, height=600):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        self.root = root

        self.sidebar_width = sidebar_width
        self.width = width
        self.height = height

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

        setup_style()

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

    def reset_focus(self):
        """
        """
        self.root.focus_set()

    def exit(self):
        # TODO ask confirmation
        self.root.destroy()

    ### REACTIONS TO OBSERVABLES ###

    def update_window_title(self, title):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_window_title")
        logg.info(f"{fmt_cn('Updating')} title '{title}'")
        self.root.title(title)


class FrameInfo(ttk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # setup grid for this frame
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create children frames
        self.font_measurement_frame = ttk.Frame(self, style="group.TFrame")
        self.spoint_adjust_frame = ttk.Frame(self, style="group.TFrame")
        self.mouse_info_frame = ttk.Frame(self, style="group.TFrame")
        self.file_save_frame = ttk.Frame(self, style="group.TFrame")

        # grid the children frames
        self.font_measurement_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.spoint_adjust_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.file_save_frame.grid(row=2, column=0, sticky="new", padx=10, pady=10)
        self.mouse_info_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)

        # build the objects in children frames
        self.build_font_measurement_frame()
        self.build_spoint_adjust_frame()
        self.build_file_save_frame()
        self.build_mouse_info_frame()

    def build_font_measurement_frame(self):
        """Build the elements inside font_measurement_frame and grid them
        """
        self.fm_title = ttk.Label(
            self.font_measurement_frame, text="Font measurement", style="title.TLabel"
        )

        self.fm_btn_set_base_mean = ttk.Button(
            self.font_measurement_frame, text="B - M", style="settings.TButton",
        )

        self.fm_btn_set_base_ascent = ttk.Button(
            self.font_measurement_frame, text="B - A", style="settings.TButton",
        )

        self.fm_btn_set_mean_descent = ttk.Button(
            self.font_measurement_frame, text="M - D", style="settings.TButton",
        )

        # setup grid for font_measurement_frame
        self.font_measurement_frame.grid_columnconfigure(0, weight=1)
        self.font_measurement_frame.grid_columnconfigure(1, weight=1)
        self.font_measurement_frame.grid_columnconfigure(2, weight=1)

        # grid the objects in font_measurement_frame
        self.fm_title.grid(row=0, column=0, sticky="ew", columnspan=3)
        self.fm_btn_set_base_mean.grid(row=1, column=0, pady=4)
        self.fm_btn_set_base_ascent.grid(row=1, column=1, pady=4)
        self.fm_btn_set_mean_descent.grid(row=1, column=2, pady=4)

    def build_spoint_adjust_frame(self):
        """Build the monster with 12 buttons
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.build_spoint_adjust_frame")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('build_spoint_adjust_frame')}")

        self.sa_title = ttk.Label(
            self.spoint_adjust_frame, text="Spline adjust", style="title.TLabel"
        )

        # setup grid for spoint_adjust_frame
        self.spoint_adjust_frame.grid_columnconfigure(0, weight=1)
        self.spoint_adjust_frame.grid_columnconfigure(1, weight=1)
        self.spoint_adjust_frame.grid_columnconfigure(2, weight=1)
        self.spoint_adjust_frame.grid_columnconfigure(3, weight=1)

        bt_sty = "settings.TButton"
        self.sa_btn_vl = ttk.Button(self.spoint_adjust_frame, text="VL", style=bt_sty)
        self.sa_btn_l = ttk.Button(self.spoint_adjust_frame, text="L", style=bt_sty)
        self.sa_btn_r = ttk.Button(self.spoint_adjust_frame, text="R", style=bt_sty)
        self.sa_btn_vr = ttk.Button(self.spoint_adjust_frame, text="VR", style=bt_sty)

        self.sa_btn_vb = ttk.Button(self.spoint_adjust_frame, text="VB", style=bt_sty)
        self.sa_btn_b = ttk.Button(self.spoint_adjust_frame, text="B", style=bt_sty)
        self.sa_btn_u = ttk.Button(self.spoint_adjust_frame, text="U", style=bt_sty)
        self.sa_btn_vu = ttk.Button(self.spoint_adjust_frame, text="VU", style=bt_sty)

        self.sa_btn_va = ttk.Button(self.spoint_adjust_frame, text="VA", style=bt_sty)
        self.sa_btn_a = ttk.Button(self.spoint_adjust_frame, text="A", style=bt_sty)
        self.sa_btn_o = ttk.Button(self.spoint_adjust_frame, text="O", style=bt_sty)
        self.sa_btn_vo = ttk.Button(self.spoint_adjust_frame, text="VO", style=bt_sty)

        self.sa_title.grid(row=0, column=0, sticky="ew", columnspan=4)

        self.sa_btn_vl.grid(row=1, column=0, padx=4, pady=4)
        self.sa_btn_l.grid(row=1, column=1, padx=4, pady=4)
        self.sa_btn_r.grid(row=1, column=2, padx=4, pady=4)
        self.sa_btn_vr.grid(row=1, column=3, padx=4, pady=4)

        self.sa_btn_vb.grid(row=2, column=0, padx=4, pady=4)
        self.sa_btn_b.grid(row=2, column=1, padx=4, pady=4)
        self.sa_btn_u.grid(row=2, column=2, padx=4, pady=4)
        self.sa_btn_vu.grid(row=2, column=3, padx=4, pady=4)

        self.sa_btn_va.grid(row=3, column=0, padx=4, pady=4)
        self.sa_btn_a.grid(row=3, column=1, padx=4, pady=4)
        self.sa_btn_o.grid(row=3, column=2, padx=4, pady=4)
        self.sa_btn_vo.grid(row=3, column=3, padx=4, pady=4)

    def build_file_save_frame(self):
        """
        """
        self.fs_title = ttk.Label(
            self.file_save_frame, text="Output path", style="title.TLabel"
        )

        self.fs_btn_save_spline = ttk.Button(
            self.file_save_frame, text="Save", style="settings.TButton",
        )

        self.fs_btn_set_save_path = ttk.Button(
            self.file_save_frame, text="Set folder", style="settings.TButton",
        )

        self.fs_lab_root = ttk.Label(
            self.file_save_frame, text="Path root:", style="info.TLabel"
        )
        self.fs_ent_root = ttk.Entry(
            self.file_save_frame,
            text="Path root:",
            style="root.TEntry",
            exportselection=0,
            width=13,
        )

        # setup grid for file_save_frame
        self.file_save_frame.grid_columnconfigure(0, weight=1, uniform="half")
        self.file_save_frame.grid_columnconfigure(1, weight=1, uniform="half")

        # grid the objects in file_save_frame
        self.fs_title.grid(row=0, column=0, sticky="ew", columnspan=2)
        self.fs_lab_root.grid(row=1, column=0, pady=4)
        self.fs_ent_root.grid(row=1, column=1, pady=4)
        self.fs_btn_set_save_path.grid(row=2, column=0, pady=4)
        self.fs_btn_save_spline.grid(row=2, column=1, pady=4)

    def build_mouse_info_frame(self):
        """Build the elements inside mouse_info_frame and grid them
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.build_mouse_info_frame")
        logg.info(f"Start {fmt_cn('build_mouse_info_frame')}")

        # mouse_info_frame title label
        self.mi_title = ttk.Label(
            self.mouse_info_frame, text="Mouse info", style="title.TLabel"
        )

        # create mouse pos info dicts to hold labels and vars
        self.mi_var_pos_info = {}
        self.mi_label_pos_info = {}

        for pos_type in ["view", "abs", "canvas", "fm"]:
            self.mi_var_pos_info[pos_type] = tk.StringVar(self.mouse_info_frame)
            self.mi_label_pos_info[pos_type] = ttk.Label(
                self.mouse_info_frame,
                textvariable=self.mi_var_pos_info[pos_type],
                style="info.TLabel",
            )
            self.mi_var_pos_info[pos_type].set(f"{pos_type.capitalize()} (0, 0)")

        # create state info label
        self.mi_var_state = tk.StringVar(self.mouse_info_frame)
        self.mi_label_state = ttk.Label(
            self.mouse_info_frame, textvariable=self.mi_var_state, style="info.TLabel",
        )
        self.mi_var_state.set("State: FREE")

        # setup grid for mouse_info_frame
        self.mouse_info_frame.grid_columnconfigure(0, weight=1)

        # grid mouse_info_frame elements
        self.mi_title.grid(row=0, column=0, sticky="ew")
        self.mi_label_pos_info["view"].grid(row=1, column=0, sticky="ew")
        self.mi_label_pos_info["abs"].grid(row=2, column=0, sticky="ew")
        self.mi_label_pos_info["canvas"].grid(row=3, column=0, sticky="ew")
        self.mi_label_pos_info["fm"].grid(row=4, column=0, sticky="ew")
        self.mi_label_state.grid(row=5, column=0, sticky="ew")

    ### REACTIONS TO OBSERVABLES ###

    def update_curr_mouse_pos_info(self, pos_info):
        logg = logging.getLogger(f"c.{__class__.__name__}.update_curr_mouse_pos_info")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('update_curr_mouse_pos_info')}")

        for pos_type in ["view", "canvas"]:
            pos_str = f"{pos_type.capitalize()} ({pos_info[pos_type][0]}, {pos_info[pos_type][1]})"
            logg.trace(f"pos_str: {pos_str}")
            self.mi_var_pos_info[pos_type].set(pos_str)
        for pos_type in ["abs", "fm"]:
            pos_str = f"{pos_type.capitalize()} ({pos_info[pos_type][0]:.4f}, {pos_info[pos_type][1]:.4f})"
            logg.trace(f"pos_str: {pos_str}")
            self.mi_var_pos_info[pos_type].set(pos_str)

    def update_state(self, state):
        """Update the label with the current state
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_state")
        logg.info(f"Start {fmt_cn('update_state')} {state}")
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
            logg.info(f"{fmt_cn('Unrecognized', 'alert')} system state {state}")
            return
        self.mi_var_state.set(state_str)


class FrameImage(ttk.Frame):
    def __init__(self, parent, name, *args, **kwargs):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

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
        logg.trace(f"Start {fmt_cn('update_crop_input_image')}")

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
        logg.trace(f"left: {left} top: {top} right: {right} bot: {bot}")
        self.image_bbox = (left, top, right, bot)

    def update_free_line(self, line_point):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_free_line")
        logg.trace(f"Start {fmt_cn('update_free_line')} {line_point}")

        if line_point is None:
            self.image_canvas.delete("free_line")
            return

        self.draw_line(line_point, tag="free_line", fill="red")

    def update_fm_lines(self, fm_lines):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_fm_lines")
        logg.trace(f"Start {fmt_cn('update_fm_lines')} {fm_lines}")

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
        logg.debug(f"Start {fmt_cn('update_click_left_start_pos')} {start_pos}")

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

    def update_visible_SP(self, data):
        """Update the drawn arrows
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_visible_SP")
        logg.trace(f"Start {fmt_cn('update_visible_SP')}")

        self.image_canvas.delete("spline_point")

        for spid in data:
            view_op, arrow_type = data[spid]
            if arrow_type == "selected":
                color = "red"
            elif arrow_type == "active":
                color = "green"
            elif arrow_type == "standard":
                color = "cyan2"
            else:
                logg.warn(f"{fmt_cn('Unrecognized', 'alert')} arrow_type: {arrow_type}")
                color = "cyan"
            self.draw_point(view_op, "spline_point", color)

    def update_visible_segment_SP(self, data):
        """TODO: what are you changing when updating visible_segment_SP?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_visible_segment_SP")
        logg.trace(f"Start {fmt_cn('update_visible_segment_SP')}")

        tag = "segment"
        self.image_canvas.delete(tag)

        for segment in data:
            seq = []
            for point in segment:
                seq.append(point.x + self.widget_shift_x)
                seq.append(point.y + self.widget_shift_y)

            # need at least two points to plot a line
            if len(seq) >= 4:
                self.image_canvas.create_line(*seq, tags=tag, fill="lime green")

    ### HELPERS ###

    def draw_point(self, view_op, tag, color="cyan", length=-1):
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
            canv_x, canv_y, end_x, end_y, tags=tag, arrow=tk.LAST, fill=color
        )

    def draw_line(self, image_point, tag, **kwargs):
        """Add a line on the point
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.draw_line")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('draw_line')}")

        # delete the old free_line in the canvas
        self.image_canvas.delete(tag)

        # the line_point are in the image coordinate
        # shift them to canvas coordinate
        #  line_point.translate(self.widget_shift_x, self.widget_shift_y)
        canv_point = translate_point_dxy(
            image_point, self.widget_shift_x, self.widget_shift_y
        )

        # compute the intersections
        admissible_inter = collide_line_box(self.image_bbox, canv_point)

        if len(admissible_inter) == 0:
            logg.trace(f"No line found inside the image")
            return
        elif len(admissible_inter) != 2:
            logg.warn(f"Weird amount of intersections found {len(admissible_inter)}")
            return

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
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        self.name = name
        super().__init__(parent, *args, **kwargs)

        # list of labels to keep track of spline headers
        self.all_SP_headers = []
        # dict of FrameSPoint
        self.all_SP_frames = {}
        self.old_selected_spid = None
        self.old_selected_header = None

        # setup grid for this frame
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # create the children frames
        self.spline_header_frame = ttk.Frame(self, style="group.TFrame")
        self.spline_list_frame = ttk.Frame(self, style="group.TFrame")
        # grid the children frames
        self.spline_header_frame.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        self.spline_list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # build the objects in children frames
        self.build_spline_header_frame()
        self.build_spline_list_frame()

    def build_spline_header_frame(self):
        """### setup frame for spline buttons and info ###
        """
        # setup grid for spline_header_frame
        self.spline_header_frame.grid_columnconfigure(0, weight=1)
        self.spline_header_frame.grid_columnconfigure(1, weight=1)

        # create the elements
        self.sh_title = ttk.Label(
            self.spline_header_frame, text="Spline options", style="title.TLabel"
        )
        self.sh_btn_new_spline = ttk.Button(
            self.spline_header_frame, text="New glyph", style="settings.TButton",
        )
        self.sh_btn_delete_SP = ttk.Button(
            self.spline_header_frame, text="Delete point", style="settings.TButton",
        )

        # grid the elements in spline_header_frame
        self.sh_title.grid(row=0, column=0, sticky="ew", columnspan=2)
        self.sh_btn_new_spline.grid(row=1, column=0, pady=4)
        self.sh_btn_delete_SP.grid(row=1, column=1, pady=4)

    def build_spline_list_frame(self):
        """### SETUP frame for spline points ###
        """
        # setup grid for spline_list_frame
        self.spline_list_frame.grid_rowconfigure(1, weight=1)
        self.spline_list_frame.grid_columnconfigure(0, weight=1)

        # header for this frame
        self.sl_title = ttk.Label(
            self.spline_list_frame, text="Spline points", style="title.TLabel"
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

        # create a fake frame to force the scroll_frame to be wide
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
        logg.info(f"Start {fmt_cn('update_all_SP')}")

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

            # update the text inside with current pos
            else:
                self.all_SP_frames[spid].update_label()

    def update_path_SP(self, data):
        """Grid the frames relative to the path/glyphs/points

        Grid
            - Headers
            - FrameSPoint
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_path_SP")
        logg.info(f"Start {fmt_cn('update_path_SP')} {data}")

        ### create headers
        # how many glyphs there are
        glyph_tot_num = len(data)
        for i in range(len(self.all_SP_headers), glyph_tot_num):
            logg.debug(f"Create header for i: {i}")

            # create the header label
            header_title = f"Glyph {i}"
            sp_header = LabelId(
                self.sl_scrollable.scroll_frame,
                i,
                text=header_title,
                style="sp_header.sp_info.TLabel",
            )

            # bind click to the header
            sp_header.bind("<Enter>", sp_header.on_enter)
            sp_header.bind("<Leave>", sp_header.on_leave)
            sp_header.bind("<Button-1>", sp_header.on_button1_press)

            # bind mouse scroll on header
            sp_header.register_scroll_func(self.sl_scrollable.on_list_scroll)

            # save it
            self.all_SP_headers.append(sp_header)

        # remove all frames from grid
        for spid, sp_frame in self.all_SP_frames.items():
            sp_frame.grid_forget()
        for sp_header in self.all_SP_headers:
            sp_header.grid_forget()

        row = 0
        for i, glyph in enumerate(data):
            self.all_SP_headers[i].grid(row=row, column=0, sticky="ew")
            row += 1
            for spid in glyph:
                self.all_SP_frames[spid].grid(row=row, column=0, sticky="ew")
                #  self.all_SP_frames[spid].grid(row=row, column=0, sticky="nsew")
                row += 1

    def update_selected_spid_SP(self, data):
        """Change the state of the point frame with corresponding spid

            - selected: the widget is selected
            - active: the mouse is inside
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_selected_spid_SP")
        logg.info(f"Start {fmt_cn('update_selected_spid_SP')} {data}")

        # if the old selected was a point
        if not self.old_selected_spid is None:
            # clear old selected state
            self.all_SP_frames[self.old_selected_spid].set_state("!selected")

        # save the point you will set
        self.old_selected_spid = data

        # if the new point is valid
        if not data is None:
            # set new one
            self.all_SP_frames[data].set_state("selected")

    def update_selected_header_SP(self, data):
        """Change the state of the header frame with given id
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.update_selected_header_SP")
        logg.info(f"Start {fmt_cn('update_selected_header_SP')} {data}")

        if not self.old_selected_header is None:
            self.all_SP_headers[self.old_selected_header].set_state("!selected")

        self.old_selected_header = data

        if not data is None:
            self.all_SP_headers[data].set_state("selected")
