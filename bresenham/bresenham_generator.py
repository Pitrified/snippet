import logging


def bresenham_generator(x0, y0, x1, y1):
    """Yields the points in a Bresenham line from (x0,y0) to (x1,y1)
    """

    # commented out for megafastperformance

    #  logline = logging.getLogger(f"{__name__}.console.generator")
    #  logline.setLevel("INFO")
    #  logline.setLevel("DEBUG")

    #  logline.debug(f"Generating ({x0}, {y0}) - ({x1}, {y1})")

    if abs(y1 - y0) < abs(x1 - x0):
        if x0 > x1:
            return add_line_low(x1, y1, x0, y0)
        else:
            return add_line_low(x0, y0, x1, y1)
    else:
        if y0 > y1:
            return add_line_high(x1, y1, x0, y0)
        else:
            return add_line_high(x0, y0, x1, y1)


def add_line_low(x0, y0, x1, y1):
    """
    """
    #  logline = logging.getLogger(f"{__name__}.console.linel")
    #  logline.setLevel("DEBUG")
    #  logline.setLevel("INFO")
    #  logline.debug("LOW")

    dx = x1 - x0
    dy = y1 - y0
    yi = 1

    if dy < 0:
        yi = -1
        dy = -dy

    D = 2 * dy - dx
    y = y0

    for x in range(x0, x1 + 1):
        #  logline.log(5, f"Mapping {x} {y}")

        yield x, y

        if D > 0:
            y = y + yi
            D = D - 2 * dx
        D = D + 2 * dy


def add_line_high(x0, y0, x1, y1):
    """
    """
    #  logline = logging.getLogger(f"{__name__}.console.lineh")
    #  logline.setLevel("INFO")
    #  logline.setLevel('DEBUG')
    #  logline.setLevel("TRACE")
    #  logline.debug("HIGH")

    dx = x1 - x0
    dy = y1 - y0
    xi = 1
    if dx < 0:
        xi = -1
        dx = -dx
    D = 2 * dx - dy
    x = x0

    for y in range(y0, y1 + 1):
        #  logline.log(5, f"Mapping {x} {y}")

        yield x, y

        if D > 0:
            x = x + xi
            D = D - 2 * dy
        D = D + 2 * dx


def setup_logger_generator(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logmoduleconsole = logging.getLogger(f"{__name__}.console")
    logmoduleconsole.propagate = False
    logmoduleconsole.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logmoduleconsole.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logmoduleconsole.log(5, 'Exceedingly verbose debug')

    return logmoduleconsole
