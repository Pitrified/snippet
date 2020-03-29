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
        logg.info(f"{fmt_cn('Start', 'start')} init")

        self.root = tk.Tk()

        ### MODEL ###
        self.model = Model()

        # register callbacks on the model observables
        self.model.pf_input_image.add_callback(self.updated_pf_input_image)
        self.model.crop_input_image.add_callback(self.updated_crop_input_image)
        self.model.free_line.add_callback(self.updated_free_line)
        self.model.curr_mouse_pos.add_callback(self.updated_curr_mouse_pos)
        self.model.fm_lines.add_callback(self.updated_fm_lines)
        self.model.click_start_pos.add_callback(self.updated_click_start_pos)

        ### VIEW  ###
        self.view = View(self.root)

        ### bind callbacks from user input

        # general keypress
        self.root.bind("<KeyRelease>", self.key_released)

        # react to canvas resize
        self.view.frame_image.image_canvas.bind("<Configure>", self.canvas_resized)

        # clicked on canvas
        self.view.frame_image.bind_canvas("<Button-1>", self.clicked_canvas)
        self.view.frame_image.bind_canvas("<ButtonRelease-1>", self.released_canvas)

        # moved mouse
        #  self.view.frame_image.bind_canvas("<B1-Motion>", self.moved_canvas_mouse)
        self.view.frame_image.bind_canvas("<Motion>", self.moved_canvas_mouse)

        ### button clicks
        self.view.frame_info.fm_btn_set_base_mean.config(
            command=self.clicked_btn_set_base_mean
        )

        # initialize the values in the model
        self.model.set_pf_input_image(pf_input_image)

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
        logg.info(f"Clicked mouse on canvas")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        self.model.save_click_canvas(event.x, event.y)

    def released_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.released_canvas")
        logg.setLevel("TRACE")
        logg.info(f"{fmt_cn('Released', 'start')} mouse on canvas")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        self.model.release_click_canvas(event.x, event.y)

    def moved_canvas_mouse(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.moved_canvas_mouse")
        #  logg.setLevel("TRACE")
        logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Moved', 'start')} mouse on canvas")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        self.model.move_canvas_mouse(event.x, event.y)

    def clicked_btn_set_base_mean(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_btn_set_base_mean")
        #  logg.setLevel("TRACE")
        #  logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Start', 'start')} clicked_btn_set_base_mean")

        self.model.click_set_base_mean()

    ###### OBSERVABLE CALLBACKS ######

    def updated_pf_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_pf_input_image")
        logg.info(f"New values received for pf_input_image: {data}")
        self.view.update_pf_input_image(data)

    def updated_crop_input_image(self, data):
        logg = logging.getLogger(f"c.{__name__}.updated_crop_input_image")
        logg.debug(f"{fmt_cn('Start', 'start')} updated_crop_input_image")
        self.view.frame_image.update_crop_input_image(data)

    def updated_free_line(self, data):
        logg = logging.getLogger(f"c.{__name__}.updated_free_line")
        logg.debug(f"{fmt_cn('Start', 'start')} updated_free_line")
        self.view.frame_image.update_free_line(data)

    def updated_curr_mouse_pos(self, data):
        """
        """
        logg = logging.getLogger(f"c.{__name__}.updated_curr_mouse_pos")
        logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Start', 'start')} updated_curr_mouse_pos")

        self.view.frame_info.update_curr_mouse_pos(data)

    def updated_fm_lines(self, data):
        logg = logging.getLogger(f"c.{__name__}.updated_fm_lines")
        logg.debug(f"{fmt_cn('Start', 'start')} updated_fm_lines")
        self.view.frame_image.update_fm_lines(data)

    def updated_click_start_pos(self, data):
        logg = logging.getLogger(f"c.{__name__}.updated_click_start_pos")
        logg.debug(f"{fmt_cn('Start', 'start')} updated_click_start_pos")
        self.view.frame_image.update_click_start_pos(data)
