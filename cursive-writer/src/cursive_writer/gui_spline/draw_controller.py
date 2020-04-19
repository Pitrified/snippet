import logging
import tkinter as tk
from pathlib import Path

from cursive_writer.gui_spline.draw_model import Model
from cursive_writer.gui_spline.draw_view import View
from cursive_writer.utils.color_utils import fmt_cn


class Controller:
    def __init__(self, pf_input_image, data_dir, thickness, colorscheme):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init')}")

        self.root = tk.Tk()

        ### MODEL ###
        self.model = Model(thickness=thickness)

        # register callbacks on the model observables
        self.model.pf_input_image.add_callback(self.updated_pf_input_image)
        self.model.data_dir.add_callback(self.updated_data_dir)
        self.model.crop_input_image.add_callback(self.updated_crop_input_image)
        self.model.free_line.add_callback(self.updated_free_line)
        self.model.curr_mouse_pos_info.add_callback(self.updated_curr_mouse_pos_info)
        self.model.fm_lines_view.add_callback(self.updated_fm_lines)
        self.model.click_left_start_pos.add_callback(self.updated_click_left_start_pos)
        self.model.state.add_callback(self.updated_state)
        self.model.all_SP.add_callback(self.updated_all_SP)
        self.model.visible_SP.add_callback(self.updated_visible_SP)
        self.model.path_SP.add_callback(self.updated_path_SP)
        self.model.selected_spid_SP.add_callback(self.updated_selected_spid_SP)
        self.model.selected_header_SP.add_callback(self.updated_selected_header_SP)
        self.model.visible_segment_SP.add_callback(self.updated_visible_segment_SP)
        self.model.thick_segment_points.add_callback(self.updated_thick_segment_points)

        ### VIEW  ###
        self.view = View(self.root, colorscheme=colorscheme)

        ### bind callbacks from user input

        # general keyboard
        self.root.bind("<KeyRelease>", self.key_released)

        # react to canvas resize
        self.view.frame_image.image_canvas.bind("<Configure>", self.canvas_resized)

        # clicked/moved/released mouse on canvas
        self.view.frame_image.bind_canvas("<Button>", self.clicked_canvas)
        self.view.frame_image.bind_canvas("<ButtonRelease>", self.released_canvas)
        self.view.frame_image.bind_canvas("<Motion>", self.moved_canvas_mouse)

        # the Entry gained/lost focus
        self.has_focus_ent_root = False
        self.view.frame_info.fs_ent_root.bind(
            "<FocusIn>", lambda e: self.focus_change_ent_root("in")
        )
        self.view.frame_info.fs_ent_root.bind(
            "<FocusOut>", lambda e: self.focus_change_ent_root("out")
        )

        # moved in/out, click on FrameSPoint
        self.view.root.bind("<<sp_frame_enter>>", self.sp_frame_entered)
        self.view.root.bind("<<sp_frame_leave>>", self.sp_frame_left)
        self.view.root.bind("<<sp_frame_btn1_press>>", self.sp_frame_btn1_pressed)
        self.view.root.bind("<<sp_header_enter>>", self.sp_header_entered)
        self.view.root.bind("<<sp_header_leave>>", self.sp_header_left)
        self.view.root.bind("<<sp_header_btn1_press>>", self.sp_header_btn1_pressed)

        ### button clicks

        ### info frame

        # font management
        self.view.frame_info.fm_btn_set_base_mean.config(
            command=lambda: self.clicked_btn_set_fm("bm")
        )
        self.view.frame_info.fm_btn_set_base_ascent.config(
            command=lambda: self.clicked_btn_set_fm("ba")
        )
        self.view.frame_info.fm_btn_set_mean_descent.config(
            command=lambda: self.clicked_btn_set_fm("md")
        )

        # output save/set path
        self.view.frame_info.fs_btn_save_spline.config(
            command=self.clicked_fs_btn_save_spline
        )
        self.view.frame_info.fs_btn_set_save_path.config(
            command=self.clicked_fs_btn_set_save_path
        )

        # load glyph
        self.view.frame_info.fl_btn_load_glyph.config(
            command=self.clicked_fl_btn_load_glyph
        )

        # move glyph
        self.view.frame_info.spla_btn_move_glyph.config(
            command=self.clicked_btn_move_glyph
        )

        # adjust frame
        self.view.frame_info.sa_btn_vl.config(
            command=lambda: self.clicked_btn_adjust("vl")
        )
        self.view.frame_info.sa_btn_l.config(
            command=lambda: self.clicked_btn_adjust("l")
        )
        self.view.frame_info.sa_btn_r.config(
            command=lambda: self.clicked_btn_adjust("r")
        )
        self.view.frame_info.sa_btn_vr.config(
            command=lambda: self.clicked_btn_adjust("vr")
        )
        self.view.frame_info.sa_btn_vb.config(
            command=lambda: self.clicked_btn_adjust("vb")
        )
        self.view.frame_info.sa_btn_b.config(
            command=lambda: self.clicked_btn_adjust("b")
        )
        self.view.frame_info.sa_btn_u.config(
            command=lambda: self.clicked_btn_adjust("u")
        )
        self.view.frame_info.sa_btn_vu.config(
            command=lambda: self.clicked_btn_adjust("vu")
        )
        self.view.frame_info.sa_btn_va.config(
            command=lambda: self.clicked_btn_adjust("va")
        )
        self.view.frame_info.sa_btn_a.config(
            command=lambda: self.clicked_btn_adjust("a")
        )
        self.view.frame_info.sa_btn_o.config(
            command=lambda: self.clicked_btn_adjust("o")
        )
        self.view.frame_info.sa_btn_vo.config(
            command=lambda: self.clicked_btn_adjust("vo")
        )

        # spline frame
        self.view.frame_spline.sh_btn_new_spline.config(
            command=self.clicked_sh_btn_new_spline
        )
        self.view.frame_spline.sh_btn_delete_SP.config(
            command=self.clicked_sh_btn_delete_SP
        )

        # initialize the values in the model
        self.model.set_pf_input_image(pf_input_image)
        self.model.data_dir.set(data_dir)

        self.model.path_SP.set([[]])
        self.model.selected_header_SP.set(0)

    def run(self):
        """Start the app and run the mainloop
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.run")
        logg.info(f"{fmt_cn('Running')} controller\n")

        self.root.mainloop()

    ###### INPUT ACTIONS ######

    def key_released(self, event):
        """Bind Key to functions
        """
        keysym = event.keysym

        # misc
        if keysym == "Escape":
            self.view.exit()

        # only adjust if the focus is not in the Entry
        if self.has_focus_ent_root is False:
            # adjust point
            if keysym == "q":
                self.clicked_btn_adjust("vl")
            elif keysym == "w":
                self.clicked_btn_adjust("l")
            elif keysym == "e":
                self.clicked_btn_adjust("r")
            elif keysym == "r":
                self.clicked_btn_adjust("vr")
            elif keysym == "a":
                self.clicked_btn_adjust("vb")
            elif keysym == "s":
                self.clicked_btn_adjust("b")
            elif keysym == "d":
                self.clicked_btn_adjust("u")
            elif keysym == "f":
                self.clicked_btn_adjust("vu")
            elif keysym == "z":
                self.clicked_btn_adjust("va")
            elif keysym == "x":
                self.clicked_btn_adjust("a")
            elif keysym == "c":
                self.clicked_btn_adjust("o")
            elif keysym == "v":
                self.clicked_btn_adjust("vo")

    def canvas_resized(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.canvas_resized")
        logg.info(f"{fmt_cn('Resized')} image_canvas")
        widget_wid = event.widget.winfo_width()
        widget_hei = event.widget.winfo_height()
        self.model.do_canvas_resize(widget_wid, widget_hei)

    def clicked_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_canvas")
        #  logg.setLevel("TRACE")
        recap = f"\n{fmt_cn('Clicked')} mouse on canvas"
        recap += f" - event: {event} event.state: {event.state}"
        recap += f" - event.x: {event.x} event.y: {event.y}"
        logg.info(recap)

        the_num = event.num
        if the_num == 1:
            logg.debug(f"Left click")
            click_type = "left_click"
        elif the_num == 2:
            logg.debug(f"Wheel click")
            click_type = "wheel_click"
            return
        elif the_num == 3:
            logg.debug(f"Right click")
            click_type = "right_click"
        elif the_num == 4:
            logg.debug(f"Scroll up")
            click_type = "scroll_up"
        elif the_num == 5:
            logg.debug(f"Scroll down")
            click_type = "scroll_down"
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} event num {the_num}")
            return

        self.model.save_click_canvas(click_type, event.x, event.y)

    def released_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.released_canvas")
        #  logg.setLevel("TRACE")
        recap = f"\n{fmt_cn('Released')} mouse on canvas"
        recap += f" - event: {event} event.state: {event.state}"
        recap += f" - event.x: {event.x} event.y: {event.y}"
        logg.info(recap)

        the_num = event.num
        if the_num == 1:
            logg.debug(f"Left click")
            click_type = "left_click"
        elif the_num == 2:
            logg.debug(f"Wheel click")
            click_type = "wheel_click"
            return
        elif the_num == 3:
            logg.debug(f"Right click")
            click_type = "right_click"
        elif the_num == 4:
            logg.debug(f"Scroll up")
            click_type = "scroll_up"
            return
        elif the_num == 5:
            logg.debug(f"Scroll down")
            click_type = "scroll_down"
            return
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} event num {the_num}")
            return

        self.model.release_click_canvas(click_type, event.x, event.y)

    def moved_canvas_mouse(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.moved_canvas_mouse")
        #  logg.setLevel("TRACE")
        #  logg.setLevel("DEBUG")
        #  logg.setLevel("INFO")
        recap = f"\n{fmt_cn('Moved')} mouse on canvas"
        recap += f" - event: {event} event.state: {event.state}"
        recap += f" - event.x: {event.x} event.y: {event.y}"
        logg.trace(recap)

        # TODO Shift+LeftMove (273): fm_lines with forced horizontal base
        # TODO add entry to set degrees of vertical line

        the_state = event.state
        # these were brutally harvested by reading the logs...
        if the_state == 16:
            logg.trace(f"Regular movement!")
            move_type = "move_free"
        elif the_state == 272:
            logg.trace(f"Click left movement!")
            move_type = "move_left_clicked"
        elif the_state == 1040:
            logg.trace(f"Click right movement!")
            move_type = "move_right_clicked"
        elif the_state == 528:
            logg.trace(f"Click wheel movement!")
            move_type = "move_wheel_clicked"
            return
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} event state {the_state}")
            return

        self.model.move_canvas_mouse(move_type, event.x, event.y)

    def clicked_btn_set_fm(self, fm_set_type):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_fm")
        #  logg.setLevel("TRACE")
        logg.info(f"\nStart {fmt_cn('clicked_btn_set_fm')}")
        logg.debug(f"fm_set_type: {fm_set_type}")
        self.model.clicked_btn_set_fm(fm_set_type)
        self.view.reset_focus()

    def clicked_sh_btn_new_spline(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_sh_btn_new_spline")
        #  logg.setLevel("TRACE")
        logg.info(f"\nStart {fmt_cn('clicked_sh_btn_new_spline')}")
        self.model.clicked_sh_btn_new_spline()
        self.view.reset_focus()

    def clicked_sh_btn_delete_SP(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_sh_btn_delete_SP")
        logg.info(f"\nStart {fmt_cn('clicked_sh_btn_delete_SP')}")
        self.model.clicked_sh_btn_delete_SP()
        self.view.reset_focus()

    def clicked_btn_move_glyph(self):
        """TODO: what is clicked_btn_move_glyph doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_move_glyph")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_btn_move_glyph', 'a2')}")
        self.model.clicked_btn_move_glyph()

    def clicked_fs_btn_save_spline(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fs_btn_save_spline")
        logg.info(f"\nStart {fmt_cn('clicked_fs_btn_save_spline')}")
        glyph_root_name = self.view.frame_info.fs_ent_root.get()
        logg.debug(f"glyph_root_name: {glyph_root_name}")
        self.model.clicked_fs_btn_save_spline(glyph_root_name)
        self.view.reset_focus()

    def clicked_fs_btn_set_save_path(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fs_btn_set_save_path")
        logg.info(f"\nStart {fmt_cn('clicked_fs_btn_set_save_path')}")
        self.view.reset_focus()

        data_dir = self.model.data_dir.get()
        logg.debug(f"data_dir: {data_dir}")
        str_data_dir = self.view.ask_folder(initialdir=data_dir)
        logg.debug(f"str_data_dir: {str_data_dir}")

        # filedialog sometimes returns an empty tuple, sometimes an empty string
        if len(str_data_dir) == 0:
            logg.info(f"Selection of data folder cancelled")
            return

        data_dir = Path(str_data_dir)
        logg.debug(f"data_dir: {data_dir}")

        self.model.clicked_fs_btn_set_save_path(data_dir)

    def clicked_fl_btn_load_glyph(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_fl_btn_load_glyph")
        logg.info(f"\nStart {fmt_cn('clicked_fl_btn_load_glyph')}")
        self.view.reset_focus()

        data_dir = self.model.data_dir.get()
        logg.debug(f"data_dir: {data_dir}")
        str_glyph_file_name = self.view.ask_file_name(initialdir=data_dir)
        logg.info(f"str_glyph_file_name: {str_glyph_file_name}")

        if len(str_glyph_file_name) == 0:
            logg.info(f"Glyph load cancelled")
            return

        path_file_name = Path(str_glyph_file_name)
        self.model.clicked_fl_btn_load_glyph(path_file_name)

    def clicked_btn_adjust(self, adjust_type):
        """Callback for buttons to adjust spline points
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_adjust")
        #  logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('clicked_btn_adjust')} {adjust_type}")
        self.model.clicked_btn_adjust(adjust_type)
        self.view.reset_focus()

    def sp_frame_entered(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_entered")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_entered')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")

        spid = event.widget.spoint.spid
        self.model.sp_frame_entered(spid)

    def sp_frame_left(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_left')}")
        logg.trace(f"Event {event} fired by {event.widget}")
        spid = event.widget.spoint.spid
        self.model.sp_frame_left(spid)

    def sp_frame_btn1_pressed(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_btn1_pressed")
        #  logg.setLevel("TRACE")
        logg.info(f"\nStart {fmt_cn('sp_frame_btn1_pressed')}")
        logg.trace(f"Event {event} fired by {event.widget}")
        spid = event.widget.spoint.spid
        self.model.sp_frame_btn1_pressed(spid)

    def sp_header_entered(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_entered")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_entered')}")
        logg.trace(f"Event {event} fired by {event.widget}")
        hid = event.widget.id_
        self.model.sp_header_entered(hid)

    def sp_header_left(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_left')}")
        logg.trace(f"Event {event} fired by {event.widget}")
        hid = event.widget.id_
        self.model.sp_header_left(hid)

    def sp_header_btn1_pressed(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_btn1_pressed")
        #  logg.setLevel("TRACE")
        logg.info(f"\nStart {fmt_cn('sp_header_btn1_pressed')}")
        logg.trace(f"Event {event} fired by {event.widget}")
        hid = event.widget.id_
        self.model.sp_header_btn1_pressed(hid)

    def focus_change_ent_root(self, change):
        """TODO: what is focus_change_ent_root doing?
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.focus_change_ent_root")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('focus_change_ent_root', 'a2')} {change}")

        if change == "in":
            logg.trace(f"Entry now has focus")
            self.has_focus_ent_root = True
        elif change == "out":
            logg.trace(f"Entry has lost focus")
            self.has_focus_ent_root = False
        else:
            logg.warn(f"{fmt_cn('Unrecognized', 'alert')} focus change {change}")
            return

    ###### OBSERVABLE CALLBACKS ######

    ### MISC ###

    def updated_pf_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_pf_input_image")
        logg.info(f"New values {fmt_cn('received')} for pf_input_image: {data}")
        title = f"Spline builder GUI - {data}"
        self.view.update_window_title(title)

    def updated_data_dir(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_data_dir")
        logg.debug(f"Start {fmt_cn('updated_data_dir', 'a2')}")
        self.view.update_data_dir(data)

    ### IMAGE CANVAS ###

    def updated_crop_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_crop_input_image")
        logg.trace(f"Start {fmt_cn('updated_crop_input_image')}")
        self.view.frame_image.update_crop_input_image(data)

    def updated_free_line(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_free_line")
        logg.trace(f"Start {fmt_cn('updated_free_line')}")
        self.view.frame_image.update_free_line(data)

    def updated_curr_mouse_pos_info(self, data):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_curr_mouse_pos_info")
        #  logg.setLevel("INFO")
        logg.trace(f"Start {fmt_cn('updated_curr_mouse_pos_info')}")

        self.view.frame_info.update_curr_mouse_pos_info(data)

    def updated_fm_lines(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_fm_lines")
        logg.trace(f"Start {fmt_cn('updated_fm_lines')}")
        self.view.frame_image.update_fm_lines(data)

    def updated_click_left_start_pos(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_click_left_start_pos")
        logg.info(f"Start {fmt_cn('updated_click_left_start_pos')}")
        self.view.frame_image.update_click_left_start_pos(data)

    def updated_state(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_state")
        logg.info(f"Start {fmt_cn('updated_state')}")
        self.view.frame_info.update_state(data)

    ### SPLINE INFO ###

    def updated_all_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_all_SP")
        logg.info(f"Start {fmt_cn('updated_all_SP')}")
        self.view.frame_spline.update_all_SP(data)

    def updated_visible_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_visible_SP")
        logg.trace(f"Start {fmt_cn('updated_visible_SP')}")
        self.view.frame_image.update_visible_SP(data)

    def updated_path_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_path_SP")
        logg.info(f"Start {fmt_cn('updated_path_SP')}")
        self.view.frame_spline.update_path_SP(data)

    def updated_selected_spid_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_selected_spid_SP")
        logg.info(f"Start {fmt_cn('updated_selected_spid_SP')}")
        self.view.frame_spline.update_selected_spid_SP(data)

    def updated_selected_header_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_selected_header_SP")
        logg.info(f"Start {fmt_cn('updated_selected_header_SP')}")
        self.view.frame_spline.update_selected_header_SP(data)

    def updated_visible_segment_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_visible_segment_SP")
        logg.trace(f"Start {fmt_cn('updated_visible_segment_SP')}")
        self.view.frame_image.update_visible_segment_SP(data)

    def updated_thick_segment_points(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_thick_segment_points")
        logg.debug(f"Start {fmt_cn('updated_thick_segment_points')}")
        self.view.frame_image.update_thick_segment_points(data)
