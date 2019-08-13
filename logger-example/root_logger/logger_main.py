import argparse
import logging


from logger_class import sample_class

def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console
    """
    logroot = logging.getLogger()
    #  logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def main():
    setup_logger()

    logmain = logging.getLogger(f"{__name__}.main")
    logmain.info("Some useful info")

    myclass = sample_class()

    logmain.debug("Create another!")
    myclass2 = sample_class()


if __name__ == "__main__":
    main()
