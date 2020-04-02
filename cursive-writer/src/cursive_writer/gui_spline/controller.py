import logging
import tkinter as tk

from view import View
from model import Model
from cursive_writer.utils.color_utils import fmt_c
from cursive_writer.utils.color_utils import fmt_cn


class Controller:
    def __init__(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        self.root = tk.Tk()

        ### MODEL ###
        self.model = Model()

        # register callbacks on the model observables
        self.model.pf_input_image.add_callback(self.updated_pf_input_image)
        self.model.crop_input_image.add_callback(self.updated_crop_input_image)
        self.model.free_line.add_callback(self.updated_free_line)
        self.model.curr_mouse_pos_info.add_callback(self.updated_curr_mouse_pos_info)
        self.model.fm_lines_view.add_callback(self.updated_fm_lines)
        self.model.click_left_start_pos.add_callback(self.updated_click_left_start_pos)
        self.model.state.add_callback(self.updated_state)
        self.model.all_SP.add_callback(self.updated_all_SP)
        self.model.visible_SP.add_callback(self.updated_visible_SP)
        self.model.active_SP.add_callback(self.updated_active_SP)
        self.model.selected_spid_SP.add_callback(self.updated_selected_spid_SP)
        self.model.selected_header_SP.add_callback(self.updated_selected_header_SP)

        ### VIEW  ###
        self.view = View(self.root)

        ### bind callbacks from user input

        # general keyboard
        self.root.bind("<KeyRelease>", self.key_released)

        # react to canvas resize
        self.view.frame_image.image_canvas.bind("<Configure>", self.canvas_resized)

        # clicked/moved/released mouse on canvas
        self.view.frame_image.bind_canvas("<Button>", self.clicked_canvas)
        self.view.frame_image.bind_canvas("<ButtonRelease>", self.released_canvas)
        self.view.frame_image.bind_canvas("<Motion>", self.moved_canvas_mouse)

        # moved in/out, click on FrameSPoint
        self.view.root.bind("<<sp_frame_enter>>", self.sp_frame_entered)
        self.view.root.bind("<<sp_frame_leave>>", self.sp_frame_left)
        self.view.root.bind("<<sp_frame_btn1_press>>", self.sp_frame_btn1_pressed)
        self.view.root.bind("<<sp_header_enter>>", self.sp_header_entered)
        self.view.root.bind("<<sp_header_leave>>", self.sp_header_left)
        self.view.root.bind("<<sp_header_btn1_press>>", self.sp_header_btn1_pressed)

        ### button clicks
        self.view.frame_info.fm_btn_set_base_mean.config(
            command=self.clicked_btn_set_base_mean
        )
        self.view.frame_info.fm_btn_set_base_ascent.config(
            command=self.clicked_btn_set_base_ascent
        )
        self.view.frame_spline.sh_btn_new_spline.config(
            command=self.clicked_sh_btn_new_spline
        )

        # initialize the values in the model
        self.model.set_pf_input_image(pf_input_image)

        self.model.active_SP.set([[]])
        self.model.selected_header_SP.set(0)

    def run(self):
        """Start the app and run the mainloop
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.run")
        logg.info(f"{fmt_cn('Running', 'start')} controller\n")

        self.root.mainloop()

    ###### INPUT ACTIONS ######

    def key_released(self, event):
        """Bind Key to functions
        """
        keysym = event.keysym

        # misc
        if keysym == "Escape":
            self.view.exit()

    def canvas_resized(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.canvas_resized")
        logg.info(f"{fmt_cn('Resized', 'start')} image_canvas")
        widget_wid = event.widget.winfo_width()
        widget_hei = event.widget.winfo_height()
        self.model.do_canvas_resize(widget_wid, widget_hei)

    def clicked_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_canvas")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Clicked', 'start')} mouse on canvas")
        logg.trace(f"event: {event} event.state: {event.state}")
        #  type(event.state): {type(event.state)}
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

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
            logg.error(f"{fmt_cn('Unrecognized', 'error')} event num {the_num}")
            return

        self.model.save_click_canvas(click_type, event.x, event.y)

    def released_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.released_canvas")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Released', 'start')} mouse on canvas")
        logg.trace(f"event: {event} event.state: {event.state}")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

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
            logg.error(f"{fmt_cn('Unrecognized', 'error')} event num {the_num}")
            return

        self.model.release_click_canvas(click_type, event.x, event.y)

    def moved_canvas_mouse(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.moved_canvas_mouse")
        #  logg.setLevel("TRACE")
        #  logg.setLevel("DEBUG")
        logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Moved', 'start')} mouse on canvas")
        logg.trace(f"event: {event} event.state: {event.state}")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        # TODO Shift+LeftMove (273): fm_lines with forced horizontal base
        # TODO add entry to set degrees of vertical line

        the_state = event.state
        # these were brutally harvested by reading the logs...
        if the_state == 16:
            logg.debug(f"Regular movement!")
            move_type = "move_free"
        elif the_state == 272:
            logg.debug(f"Click left movement!")
            move_type = "move_left_clicked"
        elif the_state == 1040:
            logg.debug(f"Click right movement!")
            move_type = "move_right_clicked"
        elif the_state == 528:
            logg.debug(f"Click wheel movement!")
            move_type = "move_wheel_clicked"
            return
        else:
            logg.error(f"{fmt_cn('Unrecognized', 'error')} event state {the_state}")
            return

        self.model.move_canvas_mouse(move_type, event.x, event.y)

    def clicked_btn_set_base_mean(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_base_mean")
        #  logg.setLevel("TRACE")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('clicked_btn_set_base_mean', 'start')}")

        self.model.clicked_btn_set_base_mean()

        self.view.reset_focus()

    def clicked_btn_set_base_ascent(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_base_ascent")
        #  logg.setLevel("TRACE")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('clicked_btn_set_base_ascent', 'start')}")

        self.model.clicked_btn_set_base_ascent()

        self.view.reset_focus()

    def clicked_sh_btn_new_spline(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_sh_btn_new_spline")
        #  logg.setLevel("TRACE")
        #  logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('clicked_sh_btn_new_spline', 'start')}")

        self.model.clicked_sh_btn_new_spline()

        self.view.reset_focus()

    def sp_frame_entered(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_entered")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_entered', 'start')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")

        spid = event.widget.spoint.spid
        self.model.sp_frame_entered(spid)

    def sp_frame_left(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_left")
        #  logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_frame_left', 'start')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")
        spid = event.widget.spoint.spid
        self.model.sp_frame_left(spid)

    def sp_frame_btn1_pressed(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_frame_btn1_pressed")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('sp_frame_btn1_pressed', 'start')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")
        spid = event.widget.spoint.spid
        self.model.sp_frame_btn1_pressed(spid)

    def sp_header_entered(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_entered")
        logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_entered', 'start')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")
        hid = event.widget.id_
        self.model.sp_header_entered(hid)

    def sp_header_left(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_left")
        logg.setLevel("TRACE")
        logg.trace(f"Start {fmt_cn('sp_header_left', 'start')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")
        hid = event.widget.id_
        self.model.sp_header_left(hid)

    def sp_header_btn1_pressed(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.sp_header_btn1_pressed")
        logg.setLevel("TRACE")
        logg.debug(f"Start {fmt_cn('sp_header_btn1_pressed', 'start')}")
        #  logg.trace(f"Event {event} fired by {event.widget}")
        hid = event.widget.id_
        self.model.sp_header_btn1_pressed(hid)

    ###### OBSERVABLE CALLBACKS ######

    ### MISC ###

    def updated_pf_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_pf_input_image")
        logg.info(
            f"New values {fmt_cn('received', 'start')} for pf_input_image: {data}"
        )
        self.view.update_pf_input_image(data)

    ### IMAGE CANVAS ###

    def updated_crop_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_crop_input_image")
        logg.debug(f"Start {fmt_cn('updated_crop_input_image', 'start')}")
        self.view.frame_image.update_crop_input_image(data)

    def updated_free_line(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_free_line")
        logg.trace(f"Start {fmt_cn('updated_free_line', 'start')}")
        self.view.frame_image.update_free_line(data)

    def updated_curr_mouse_pos_info(self, data):
        """
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_curr_mouse_pos_info")
        logg.setLevel("INFO")
        logg.debug(f"Start {fmt_cn('updated_curr_mouse_pos_info', 'start')}")

        self.view.frame_info.update_curr_mouse_pos_info(data)

    def updated_fm_lines(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_fm_lines")
        logg.debug(f"Start {fmt_cn('updated_fm_lines', 'start')}")
        self.view.frame_image.update_fm_lines(data)

    def updated_click_left_start_pos(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_click_left_start_pos")
        logg.debug(f"Start {fmt_cn('updated_click_left_start_pos', 'start')}")
        self.view.frame_image.update_click_left_start_pos(data)

    def updated_state(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_state")
        logg.debug(f"Start {fmt_cn('updated_state', 'start')}")
        self.view.frame_info.update_state(data)

    ### SPLINE INFO ###

    def updated_all_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_all_SP")
        logg.debug(f"Start {fmt_cn('updated_all_SP', 'start')}")
        self.view.frame_spline.update_all_SP(data)

    def updated_visible_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_visible_SP")
        logg.trace(f"Start {fmt_cn('updated_visible_SP', 'start')}")
        self.view.update_visible_SP(data)

    def updated_active_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_active_SP")
        logg.debug(f"Start {fmt_cn('updated_active_SP', 'start')}")
        self.view.frame_spline.update_active_SP(data)

    def updated_selected_spid_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_selected_spid_SP")
        logg.debug(f"Start {fmt_cn('updated_selected_spid_SP', 'start')}")
        self.view.frame_spline.update_selected_spid_SP(data)

    def updated_selected_header_SP(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_selected_header_SP")
        logg.debug(f"Start {fmt_cn('updated_selected_header_SP', 'start')}")
        self.view.frame_spline.update_selected_header_SP(data)
