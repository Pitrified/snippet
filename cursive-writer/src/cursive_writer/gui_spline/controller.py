import logging
import tkinter as tk

from view import View
from model import Model


class Controller:
    def __init__(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info("Start init")

        self.root = tk.Tk()

        ### MODEL ###
        self.model = Model()

        # register callbacks on the model observables
        self.model.pf_input_image.add_callback(self.updated_pf_input_image)
        self.model.crop_input_image.add_callback(self.updated_crop_input_image)
        self.model.free_line.add_callback(self.updated_free_line)
        self.model.curr_mouse_pos.add_callback(self.updated_curr_mouse_pos)

        ### VIEW  ###
        self.view = View(self.root)

        # bind callbacks from user input

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

        # initialize the values in the model
        self.model.set_pf_input_image(pf_input_image)

    def run(self):
        """Start the app and run the mainloop
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.run")
        logg.info("Running controller\n")

        self.root.mainloop()

    def key_released(self, event):
        """Bind Key to functions
        """
        keysym = event.keysym

        # misc
        if keysym == "Escape":
            self.view.exit()

    def updated_pf_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_pf_input_image")
        logg.info(f"New values received for pf_input_image: {data}")
        self.view.update_pf_input_image(data)

    def canvas_resized(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.canvas_resized")
        logg.info(f"Resized image_canvas")
        widget_wid = event.widget.winfo_width()
        widget_hei = event.widget.winfo_height()
        self.model.do_canvas_resize(widget_wid, widget_hei)

    def updated_crop_input_image(self, data):
        logg = logging.getLogger(f"c.{__name__}.updated_crop_input_image")
        logg.debug(f"Start updated_crop_input_image")
        self.view.frame_image.update_crop_input_image(data)

    def clicked_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.clicked_canvas")
        logg.setLevel("TRACE")
        logg.info(f"Clicked mouse on canvas")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        self.model.save_click_canvas(event.x, event.y)

    def released_canvas(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.released_canvas")
        logg.setLevel("TRACE")
        logg.info(f"Released mouse on canvas")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        self.model.release_click_canvas(event.x, event.y)

    def moved_canvas_mouse(self, event):
        logg = logging.getLogger(f"c.{__class__.__name__}.moved_canvas_mouse")
        logg.setLevel("TRACE")
        logg.info(f"Moved mouse on canvas")
        logg.trace(f"event.x: {event.x} event.y: {event.y}")

        self.model.move_canvas_mouse(event.x, event.y)

    def updated_free_line(self, data):
        logg = logging.getLogger(f"c.{__name__}.updated_free_line")
        logg.debug(f"Start updated_free_line")
        self.view.frame_image.update_free_line(data)

    def updated_curr_mouse_pos(self, data):
        """
        """
        logg = logging.getLogger(f"c.{__name__}.updated_curr_mouse_pos")
        logg.debug(f"Start updated_curr_mouse_pos")
        # TODO update some label in the view

