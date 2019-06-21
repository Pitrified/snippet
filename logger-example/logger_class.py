import logging

class sample_class:
    def __init__(self):
        '''initialize the logger here
        '''
        self.setup_class_logger()

    def setup_class_logger(self):
        '''show use of a separate logger for a module
        '''
        #  class_console_logger = logging.getLogger(f'{__name__}.console')
        class_console_logger = logging.getLogger(f'{self.__class__.__name__}.console')
        class_console_logger.propagate = False

        class_console_logger.setLevel('DEBUG')

        module_console_handler = logging.StreamHandler()

        log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format_module)
        module_console_handler.setFormatter(formatter)

        class_console_logger.addHandler(module_console_handler)

        class_console_logger.debug(f'My module name is {__name__}')
        class_console_logger.debug(f'My class is {self.__class__}')
        class_console_logger.debug(f'My class name is {self.__class__.__name__}')


