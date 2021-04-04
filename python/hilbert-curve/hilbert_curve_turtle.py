"""Draw the Hilbert curve with turtle."""
import argparse
import logging
from pathlib import Path
import turtle
import typing as ty


class HilberTurtle:
    def __init__(self, level: int) -> None:
        r"""Setup a HilberTurtle."""
        logg = logging.getLogger(f"c.{__name__}.__init__")
        logg.debug("Start __init__")

        # save the max recursion level
        self.max_level = level

        # setup the screen
        self.WIDTH = max(20 * 2 ** self.max_level, 400)
        self.HEIGHT = max(20 * 2 ** self.max_level, 400)
        self.screen = turtle.Screen()
        self.screen.setup(self.WIDTH + 4, self.HEIGHT + 8)
        self.screen.setworldcoordinates(0, 0, self.WIDTH, self.HEIGHT)
        # do not draw the screen constantly, only with screen.update()
        self.screen.tracer(False)

        # setup the turtle
        self.t = turtle.Turtle()
        self.t.pendown()
        turtle.bgcolor("#989694")

        # setup the production rules
        self.A = "+BF-AFA-FB+"
        self.B = "-AF+BFB+FA-"

        # add a callback to start drawing
        turtle.listen()
        turtle.onkeypress(self.draw, "s")

        # create a logger for draw to avoid calling it a zillion times
        self.ldraw: logging.Logger = logging.getLogger(f"c.{__name__}.draw")
        self.draw_count = 0

    def start(self) -> None:
        r"""Start the mainloop."""
        turtle.mainloop()

    def forward(self, dist: float):
        r"""Move the turtle forward."""
        self.t.forward(dist)

    def turnleft(self, angle: float):
        r"""Turn the turtle left."""
        self.t.setheading(self.t.heading() + angle)

    def turnright(self, angle: float):
        r"""Turn the turtle right."""
        self.t.setheading(self.t.heading() - angle)

    def draw(self, level: int = -1):
        """Draw the curve.

        The trick to avoid creating the entire instruction string is doing a depth first
        approach, substituting immediately the AB char.
        Adding "|" when rewriting the string is an easy way to keep track of the
        recursion levels.
        """
        self.ldraw.debug(f"Start draw {level}")
        self.draw_count += 1

        if level == -1:
            # setup the initial level of the curve
            level = self.max_level
            # setup the initial todo list
            self.remaining = self.A

        while len(self.remaining) > 0:
            cur_char = self.remaining[0]
            self.remaining = self.remaining[1:]
            self.ldraw.debug(f"lev {level} cur_char {cur_char} rem {self.remaining}")

            if cur_char == "|":
                if level + 6 > self.max_level:
                    self.screen.update()
                return

            elif cur_char == "+":
                self.turnleft(90)

            elif cur_char == "-":
                self.turnright(90)

            elif cur_char == "F":
                self.forward(10)

            elif cur_char == "A":
                if level > 0:
                    self.remaining = self.A + "|" + self.remaining
                    self.draw(level - 1)

            elif cur_char == "B":
                if level > 0:
                    self.remaining = self.B + "|" + self.remaining
                    self.draw(level - 1)

        self.screen.update()
        self.ldraw.debug(f"Done draw {level} {self.draw_count}")


def parse_arguments() -> argparse.Namespace:
    r"""Setup CLI interface.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="")

    default = "WARN"
    parser.add_argument(
        "--console_log_level",
        type=str,
        default=default,
        help=f"Level for the console logger, default {default}",
        choices=["DEBUG", "INFO", "WARN", "ERROR", "CRITICAL"],
    )

    default = "lnm"
    parser.add_argument(
        "--console_fmt_type",
        type=str,
        default=default,
        help=f"Message format for the console logger, default {default}",
        choices=["lanm", "lnm", "lm", "nm", "m"],
    )

    def_int = 5
    parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=def_int,
        help=f"Curve level, default {def_int}",
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(
    console_fmt_type: str = "m",
    console_log_level: str = "WARN",
    ui_fmt_type: ty.Optional[str] = None,
    ui_log_level: str = "INFO",
    file_fmt_type: ty.Optional[str] = None,
    file_log_level: str = "WARN",
    file_log_path: ty.Optional[Path] = None,
    file_log_mode: str = "a",
) -> None:
    r"""Setup loggers for the module.

    Args:
        console_fmt_type: Message format for the console logger.
        console_log_level: Logger level for the console logger.
    """
    # setup the format strings
    format_types = {}
    format_types["lanm"] = "[%(levelname)-8s] %(asctime)s %(name)s: %(message)s"
    format_types["lnm"] = "[%(levelname)-8s] %(name)s: %(message)s"
    format_types["lm"] = "[%(levelname)-8s]: %(message)s"
    format_types["nm"] = "%(name)s: %(message)s"
    format_types["m"] = "%(message)s"

    # setup the console handler with the console formatter
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(format_types[console_fmt_type])
    console_handler.setFormatter(console_formatter)

    # setup the console logger with the console handler
    logconsole = logging.getLogger("c")
    logconsole.propagate = False
    logconsole.setLevel(console_log_level)
    logconsole.addHandler(console_handler)


def setup_env() -> argparse.Namespace:
    r"""Setup the logger and parse the args.

    Returns:
        The parsed arguments.
    """
    # parse the command line arguments
    args = parse_arguments()

    # setup the loggers
    console_fmt_type = args.console_fmt_type
    console_log_level = args.console_log_level
    setup_logger(console_fmt_type=console_fmt_type, console_log_level=console_log_level)

    # build command string to repeat this run, useful to remember default values
    # if an option is a flag this does not work (can't just copy/paste), sorry
    recap = "python3 sample_logger.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"
    logg = logging.getLogger(f"c.{__name__}.setup_env")
    logg.info(recap)

    return args


def run_hilbert_curve_turtle(args: argparse.Namespace) -> None:
    r"""Draw the Hilbert curve with turtle.

    Serious production rules:

        A → +BF−AFA−FB+
        B → −AF+BFB+FA−

    Args:
        args: The parsed cmdline arguments.
    """
    logg = logging.getLogger(f"c.{__name__}.run_hilbert_curve_turtle")
    logg.debug("Starting run_hilbert_curve_turtle")

    ht = HilberTurtle(args.level)
    ht.start()


if __name__ == "__main__":
    args = setup_env()
    run_hilbert_curve_turtle(args)
