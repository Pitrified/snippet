import logging


class sample_class:
    def __init__(self):
        loginit = logging.getLogger(f"{__name__}.init")
        loginit.info('Some useful info in the class')

