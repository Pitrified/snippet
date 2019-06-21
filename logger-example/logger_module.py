import logging

def setup_module_logger():
    '''show use of a separate logger for a module
    '''
    module_console_logger = logging.getLogger(f'{__name__}.console')
    module_console_logger.propagate = False

    module_console_logger.setLevel('DEBUG')

    module_console_handler = logging.StreamHandler()

    log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    module_console_logger.addHandler(module_console_handler)

    module_console_logger.debug(f'My module name is {__name__}')

def test_exception_logger():
    '''show hot to print the stack trace
    '''
    # no setup is needed, just use the module level console logger
    module_console_logger = logging.getLogger(f'{__name__}.console')

    try:
        1/0
    except ZeroDivisionError as e:
        module_console_logger.exception('This failed, as you feared:')

def test_multiple_handlers():
    '''you can have multiple handlers attached to the same logger
    '''

    multiple_logger = logging.getLogger(f'{__name__}.multiple')
    multiple_logger.propagate = False

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler('module_logs.log', mode='w')

    # they can have different log levels
    c_handler.setLevel(logging.WARNING) # the console WILL print the warning
    f_handler.setLevel(logging.ERROR)   # the file will only log errors

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    multiple_logger.addHandler(c_handler)
    multiple_logger.addHandler(f_handler)

    multiple_logger.warning('This is a warning from the module')
    multiple_logger.error('This is an error from the module')

