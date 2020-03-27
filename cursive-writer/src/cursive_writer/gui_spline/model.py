import logging

from observable import Observable


class Model:
    def __init__(self):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.setLevel("TRACE")
        logg.info("Start init")

        self.pf_input_image = Observable(None)
        self.crop_input_image = Observable(None)

    def set_input_image(self, pf_input_image):
        logg = logging.getLogger(f"c.{__class__.__name__}.set_input_image")
        logg.info(f"Setting pf_input_image '{pf_input_image}'")

        self.pf_input_image.set(pf_input_image)

        self._image = Image.open(self.pf_input_image.get())
