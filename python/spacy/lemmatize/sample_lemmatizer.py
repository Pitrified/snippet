"""Sample use of lemmatizer and sentence splitter.

https://www.projectpro.io/recipes/use-spacy-lemmatizer
https://stackabuse.com/python-for-nlp-tokenization-stemming-and-lemmatization-with-spacy-library/
"""
import argparse
import logging
from pathlib import Path
import typing as ty

import spacy  # type: ignore


# from timeit import default_timer as timer
# import numpy as np  # type: ignore


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

    # last line to parse the args
    args = parser.parse_args()
    return args


def setup_logger(console_fmt_type: str = "m", console_log_level: str = "WARN") -> None:
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


def run_sample_lemmatizer(args: argparse.Namespace) -> None:
    r"""MAKEDOC: What is sample_lemmatizer doing?

    Args:
        args: The parsed cmdline arguments.
    """
    logg = logging.getLogger(f"c.{__name__}.run_sample_lemmatizer")
    logg.setLevel("DEBUG")
    logg.debug("Starting run_sample_lemmatizer")

    # nlp_en = spacy.load("en_core_web_sm")
    # doc1 = nlp_en("Manchester United isn't looking to sign a forward for $90 million.")
    # doc2 = nlp_en(
    #     "Hello from Stackabuse."
    #     " The site with the best Python Tutorials."
    #     " What are you looking for?"
    # )

    nlp_fr = spacy.load("fr_core_news_sm")
    doc3 = nlp_fr(
        "Le rouge est une couleur vive."
        " C’est la couleur de nombreux fruits et légumes, comme les tomates, les fraises ou les cerises."
        " Le jaune est la couleur des bananes, du maïs ou des poussins par exemple."
        " Le bleu est très présent dans la nature : c’est la couleur du ciel et de la mer."
        " Le rouge, le jaune et le bleu sont les trois couleurs primaires."
    )

    doc = doc3

    print(f"{doc=}")
    print(f"{type(doc)=}")
    for word in doc:
        recap = f"{word.text=:<12s}"
        recap += f" {word.lemma_=:<12s}"
        recap += f" {word.pos_=:<8s} {word.dep_=:<10s}"
        recap += f" word.is_sent_start={str(word.is_sent_start):<6s}"
        recap += f" word.is_sent_end={str(word.is_sent_end):<6s}"
        recap += f" {type(word)=}"
        print(recap)

    print()

    # a doc can easily be split in sentences
    for sentence in doc.sents:
        print(f"{sentence}")


if __name__ == "__main__":
    args = setup_env()
    run_sample_lemmatizer(args)
