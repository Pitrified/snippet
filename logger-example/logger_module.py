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

