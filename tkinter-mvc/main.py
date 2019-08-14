import logging
import tkinter as tk

from view import View
from controller import Controller


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    #  logroot = logging.getLogger()
    logroot = logging.getLogger("c")
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    log_format_module = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = "%(name)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def test_view():
    root = tk.Tk()
    width = 600
    height = 400
    #  root.geometry(f"{width}x{height}")
    v = View(root)
    root.mainloop()


def test_run():
    c = Controller()
    c.run()


def main():
    setup_logger()
    #  setup_logger("INFO")

    recap = f"python3 main.py"

    logmain = logging.getLogger(f"c.{__name__}.main")
    logmain.info(recap)

    #  test_view()
    test_run()


if __name__ == "__main__":
    main()
