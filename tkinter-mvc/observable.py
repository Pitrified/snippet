import logging


class Observable:
    """A wrapper around data, to link callbacks to it
    """

    def __init__(self, initialValue=None):
        log = logging.getLogger(f"c.{__name__}.init")
        log.debug('Start init')

        self.data = initialValue
        self.callbacks = {}

    def addCallback(self, func):
        self.callbacks[func] = 1

    def delCallback(self, func):
        del self.callback[func]

    def _docallbacks(self):
        for func in self.callbacks:
            func(self.data)

    def set(self, data):
        self.data = data
        self._docallbacks()

    def get(self):
        return self.data

    def unset(self):
        self.data = None
