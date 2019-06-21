# good guides
# https://www.pylenin.com/blogs/python-logging-guide/
# https://realpython.com/python-logging/

import logging
from logger_module import test_module_logger

def setup_logger():
    '''setup the loggers for the main module

    a main_logger that prints to file
    a console_logger that prints to console
    '''

    ###########################################################################

    # get the main logger
    main_logger = logging.getLogger(__name__)

    # To override the default severity of logging
    main_logger.setLevel('DEBUG')

    # Use FileHandler() to log to a file
    file_handler = logging.FileHandler('main_logs.log',
            mode='w', #default is 'a'
            )

    # set a specific format for this log (better for this handler)
    log_format_file = "%(asctime)s::%(levelname)s::%(name)s::"\
             "%(filename)s::%(lineno)d::%(message)s"
    formatter = logging.Formatter(log_format_file)
    file_handler.setFormatter(formatter)

    # Don't forget to add the file handler
    main_logger.addHandler(file_handler)
    main_logger.info("I am a separate main_logger")


    ###########################################################################

    # setup the console logger
    console_logger = logging.getLogger(f'{__name__}.console')
    console_logger.setLevel('INFO')

    # we need to stop the propagation of the messages to the parent logger
    console_logger.propagate = False

    # StreamHandler to print to console
    console_handler = logging.StreamHandler()

    # format the console output
    log_format_console = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format_console)
    console_handler.setFormatter(formatter)

    # add the handler to the logger
    console_logger.addHandler(console_handler)

    # this will not be printed
    console_logger.debug(f'My name is {__name__}')
    # this will be printed
    console_logger.info(f'My name is {__name__}!!!')

def test_child_logger():
    '''show an example of child logger

    it inherits all the properties of the parents, so no setup is needed
    this is very useful to turn on/off debug statement on a per function basis
    '''
    # .child will have .console as parent
    child_logger = logging.getLogger(f'{__name__}.console.child')
    child_logger.setLevel('DEBUG')

    child_logger.debug(f'Debug me')

def test_verbose_logger():
    '''show a second console logger to have different print stream

    just raise the level above any message you print with the verbose logger
    '''
    # you can have as many as you want
    # I have doubts: is making this a child of console useful at all?
    verbose_logger = logging.getLogger(f'{__name__}.console.verbose')

    # but don't propagate up this messages
    verbose_logger.propagate = False
    verbose_logger.setLevel('DEBUG')

    # change the formatting as needed, you need a new handler
    verbose_handler = logging.StreamHandler()

    log_format_verbose = 'Verbose:\n%(message)s'
    formatter = logging.Formatter(log_format_verbose)
    verbose_handler.setFormatter(formatter)

    # and remember to add it to the logger
    verbose_logger.addHandler(verbose_handler)

    from random import random
    long_list = [f'{random():.4f}' for _ in range(10)]
    verbose_logger.debug(long_list)

def main():
    '''examples of logging modules
    '''
    setup_logger()
    test_child_logger()
    test_verbose_logger()
    test_module_logger()

if __name__ == '__main__':
    main()
