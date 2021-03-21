import logging

from cursive_writer.utils.color_utils import fmt_cn


class Observable:
    """A wrapper around data, to link callbacks to it
    """

    def __init__(self, initialValue=None):
        logg = logging.getLogger(f"c.{__class__.__name__}.init")
        logg.info(f"Start {fmt_cn('init', 'start')}")

        self.data = initialValue
        self.callbacks = {}

    def add_callback(self, func):
        logg = logging.getLogger(f"c.{__class__.__name__}.add_callback")
        logg.info(f"{fmt_cn('Adding', 'start')} callback")

        self.callbacks[func] = 1

    def del_callback(self, func):
        del self.callback[func]

    def _docallbacks(self):
        for func in self.callbacks:
            func(self.data)

    def set(self, data):
        logg = logging.getLogger(f"c.{__class__.__name__}.set")
        logg.setLevel("INFO")
        logg.debug(f"{fmt_cn('Setting', 'start')} data")

        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None
