import logging
import tkinter as tk
from random import seed

from scrollable_frame import ScrollableFrame

def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
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


def test_scrollable_frame():
    root = tk.Tk()

    # the row expands
    root.grid_rowconfigure(0, weight=1)
    # the first column expands
    root.grid_columnconfigure(0, weight=1)
    # the second column is fixed (set only for clarity)
    root.grid_columnconfigure(1, weight=0)

    # create the ScrollableFrame, with a set width
    scroll_width = 200
    scroll = ScrollableFrame(root, scroll_width=scroll_width)
    scroll.grid(row=0, column=1, sticky="ns")

    # the main windows is here, this does expand 'ew'
    filler = tk.Frame(root, bg="blue", width=100)
    filler.grid(row=0, column=0, sticky="nsew")

    labels = []
    for i in range(30):
        new_label = tk.Label(
            scroll.scroll_frame,
            text=f"Label created at row {i}",
            background="orange",
        )
        new_label.grid(row=i, column=0, sticky="ew")

        # add bindings for mouse scrolling
        new_label.bind("<4>", scroll.on_list_scroll)
        new_label.bind("<5>", scroll.on_list_scroll)
        new_label.bind("<MouseWheel>", scroll.on_list_scroll)

        labels.append(new_label)

    # if the labels do not cover the entire canvas, some of these might work
    #  scroll.bind("<4>", scroll.on_list_scroll)
    #  scroll.bind("<5>", scroll.on_list_scroll)
    #  scroll.bind("<MouseWheel>", scroll.on_list_scroll)

    #  scroll.scroll_canvas.bind("<4>", scroll.on_list_scroll)
    #  scroll.scroll_canvas.bind("<5>", scroll.on_list_scroll)
    #  scroll.scroll_canvas.bind("<MouseWheel>", scroll.on_list_scroll)

    #  scroll.scroll_frame.bind("<4>", scroll.on_list_scroll)
    #  scroll.scroll_frame.bind("<5>", scroll.on_list_scroll)
    #  scroll.scroll_frame.bind("<MouseWheel>", scroll.on_list_scroll)

    root.mainloop()


def main():
    setup_logger()
    test_scrollable_frame()


if __name__ == "__main__":
    main()
