import argparse
import logging
import re
from pathlib import Path

from typing import Dict, Set, Tuple


def parse_arguments():
    """Setup CLI interface
    """
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-i",
        "--path_input",
        type=str,
        default="hp.jpg",
        help="path to input image to use",
    )

    parser.add_argument(
        "-s", "--rand_seed", type=int, default=-1, help="random seed to use"
    )

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(logLevel="DEBUG"):
    """Setup logger that outputs to console for the module
    """
    logroot = logging.getLogger("c")
    logroot.propagate = False
    logroot.setLevel(logLevel)

    module_console_handler = logging.StreamHandler()

    #  log_format_module = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #  log_format_module = "%(name)s - %(levelname)s: %(message)s"
    #  log_format_module = '%(levelname)s: %(message)s'
    #  log_format_module = '%(name)s: %(message)s'
    log_format_module = "%(message)s"

    formatter = logging.Formatter(log_format_module)
    module_console_handler.setFormatter(formatter)

    logroot.addHandler(module_console_handler)

    logging.addLevelName(5, "TRACE")
    # use it like this
    # logroot.log(5, 'Exceedingly verbose debug')


def setup_env():
    setup_logger()

    args = parse_arguments()

    # build command string to repeat this run
    # FIXME if an option is a flag this does not work, sorry
    recap = "python3 checker.py"
    for a, v in args._get_kwargs():
        recap += f" --{a} {v}"

    logmain = logging.getLogger(f"c.{__name__}.setup_env")
    logmain.info(recap)

    return args


def check_in(known: Dict[str, Set[str]], word: str) -> bool:
    """TODO: what is check_in doing?
    """
    # logg = logging.getLogger(f"c.{__name__}.check_in")
    # logg.debug("Start check_in")

    for lab in known:
        if word in known[lab]:
            return True
    return False


def run_checker(args) -> None:
    """TODO: What is checker doing?
    """
    logg = logging.getLogger(f"c.{__name__}.run_checker")
    logg.debug("Starting run_checker")

    duo_path = Path("./duolingo_course.tex")

    # structure regex
    re_chap = re.compile("\\\\chapter{(.*)}")
    re_sec = re.compile("\\\\section{(.*)}")

    # dictionary regex
    re_noundef = re.compile("\\\\noundef{(.*?)}{(.*?)}")
    re_noundecl = re.compile("\\\\noundecl{(.*?)}{(.*?)}{(.*?)}{(.*?)}")

    # save the dictionary by topic
    fr_known: Dict[str, Set[str]] = {"misc": set(), "nouns": set()}
    # where is the word defined
    fr_where: Dict[str, Tuple[str, str]] = {}

    # the current chapter and section
    this_chap = "start"
    this_sec = "start"

    with duo_path.open() as df:
        for line in df:
            line = line.rstrip()

            m_chap = re.match(re_chap, line)
            if m_chap is not None:
                # logg.debug(f"m_chap[1]: {m_chap[1]}")
                this_chap = m_chap[1]

            m_sec = re.match(re_sec, line)
            if m_sec is not None:
                # logg.debug(f"m_sec[1]: {m_sec[1]}")
                this_sec = m_sec[1]

            m_noundef = re.match(re_noundef, line)
            if m_noundef is not None:
                # logg.debug(f"m_noundef[1]: {m_noundef[1]}")
                # logg.debug(f"m_noundef[2]: {m_noundef[2]}")

                # already seen this noun
                for im in range(1, 2 + 1):
                    if m_noundef[im] in fr_known["nouns"]:
                        logg.debug(
                            f"Redefining {m_noundef[im]} in {this_chap} - {this_sec}"
                        )
                        logg.debug(f"\tSeen in {fr_where[m_noundef[im]]}")

                    else:
                        fr_known["nouns"].add(m_noundef[im])
                        fr_where[m_noundef[im]] = (this_chap, this_sec)

            m_noundecl = re.match(re_noundecl, line)
            if m_noundecl is not None:
                for im in range(1, 2 + 1):
                    if m_noundecl[im] in fr_known["nouns"]:
                        logg.debug(
                            f"Redefining {m_noundecl[im]} in {this_chap} - {this_sec}"
                        )
                        logg.debug(f"\tSeen in {fr_where[m_noundecl[im]]}")
                    else:
                        fr_known["nouns"].add(m_noundecl[im])
                        fr_where[m_noundecl[im]] = (this_chap, this_sec)


if __name__ == "__main__":
    args = setup_env()
    run_checker(args)
