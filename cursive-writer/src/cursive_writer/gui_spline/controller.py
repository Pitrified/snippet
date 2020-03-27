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
        self.model.pf_input_image.add_callback(self.updated_input_image)

        ### VIEW  ###
        self.view = View(self.root)

        # bind callbacks from user input

        # general keypress
        self.root.bind("<KeyRelease>", self.KeyReleased)

        # initialize the values in the model
        self.model.set_input_image(pf_input_image)

    def run(self):
        """Start the app and run the mainloop
        """
        logg = logging.getLogger(f"c.{__class__.__name__}.run")
        logg.info("Running controller\n")

        self.root.mainloop()

    def KeyReleased(self, event):
        """Bind Key to functions
        """
        keysym = event.keysym

        # misc
        if keysym == "Escape":
            self.view.exit()

    def updated_input_image(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.updated_input_image")
        logg.info(f"New values received for pf_input_image: {data}")
        self.view.update_input_image(data)
