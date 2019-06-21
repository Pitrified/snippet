# good guides
# https://www.pylenin.com/blogs/python-logging-guide/
# https://realpython.com/python-logging/

import logging

def setup_logger():
    '''setup the loggers for the main module

    a main_logger that prints to file
    a console_logger that prints to console
    '''

    #################################################################

    # get the main logger
    main_logger = logging.getLogger(__name__)

    # To override the default severity of logging
    main_logger.setLevel('DEBUG')

    # Use FileHandler() to log to a file
    file_handler = logging.FileHandler("main_logs.log")

    # set a specific format for this log (better for this handler)
    log_format_file = "%(asctime)s::%(levelname)s::%(name)s::"\
             "%(filename)s::%(lineno)d::%(message)s"
    formatter = logging.Formatter(log_format_file)
    file_handler.setFormatter(formatter)

    # Don't forget to add the file handler
    main_logger.addHandler(file_handler)
    main_logger.info("I am a separate main_logger")

    #################################################################

    # setup the console logger
    console_logger = logging.getLogger(f'{__name__}.console')
    console_logger.setLevel('DEBUG')

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
    console_logger.info(f'My name is {__name__}')

def main():
    '''examples of logging modules
    '''
    setup_logger()

if __name__ == '__main__':
    main()
