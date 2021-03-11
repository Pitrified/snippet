"""Download and parse the wikitionary to extract word pairs."""
import argparse
import json
import logging
from pathlib import Path
import string

from bs4 import BeautifulSoup  # type: ignore
import requests


def parse_arguments() -> argparse.Namespace:
    r"""Build the CLI interface.

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

    default = "m"
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


def setup_logger(
    console_fmt_type: str = "m",
    console_log_level: str = "WARN",
) -> None:
    r"""Build a logger for the module.

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
    r"""Build the logger and parse the args.

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


def download_pages() -> None:
    r"""Download the word list from the wikitionary."""
    logg = logging.getLogger(f"c.{__name__}.download_pages")
    # logg.setLevel("DEBUG")
    logg.debug("Start download_pages")

    url_template = "https://en.wiktionary.org/wiki/User:Matthias_Buchmeier/en-fr-{}"
    raw_name_template = "en_fr_{}.html"
    raw_data_folder = Path(__file__).absolute().parent / "data_raw"
    if not raw_data_folder.exists():
        raw_data_folder.mkdir()

    s = requests.Session()

    for letter in string.ascii_lowercase:
        logg.debug(f"letter: {letter}")
        url_wiki = url_template.format(letter)
        logg.info(f"url_wiki: {url_wiki}")
        file_name = raw_name_template.format(letter)
        file_path = raw_data_folder / file_name
        logg.debug(f"file_path: {file_path}")

        if file_path.exists():
            continue

        r = s.get(url_wiki)

        file_path.write_text(r.text)


def parse_pages() -> None:
    r"""Parse the word list and extract one-word pairs."""
    logg = logging.getLogger(f"c.{__name__}.parse_pages")
    # logg.setLevel("DEBUG")
    logg.debug("Start parse_pages")

    # the downloaded pages folder
    raw_name_template = "en_fr_{}.html"
    raw_data_folder = Path(__file__).absolute().parent / "data_raw"

    # the parsed word pairs folder
    pairs_name_template = "en_fr_{}.json"
    pairs_data_folder = Path(__file__).absolute().parent / "data_pairs"
    if not pairs_data_folder.exists():
        pairs_data_folder.mkdir()

    for letter in string.ascii_lowercase[:]:
        file_name = raw_name_template.format(letter)
        file_path = raw_data_folder / file_name
        logg.info(f"file_path: {file_path}")

        # build the path for the output
        pairs_path = pairs_data_folder / pairs_name_template.format(letter)
        if pairs_path.exists():
            continue

        word_pairs = {}

        # load and parse the page
        raw_page = file_path.read_text()
        soup = BeautifulSoup(raw_page, features="html.parser")
        content = soup.find(id="mw-content-text")
        table_rows = content.find_all("tr")

        for pair in table_rows:
            words = pair.find_all("a")
            # logg.debug(f"words: {words}")

            # check that the pair is full
            if len(words) < 2:
                logg.debug(f"Missing words: {words}")
                continue

            # if "title" not in words[0] or "title" not in words[1]:
            if not words[0].has_attr("title"):
                logg.debug(f"Missing title 0: {words[0]}")
                continue

            # the first word is always single
            word0: str = words[0]["title"]
            if word0.endswith(" (page does not exist)"):
                word0 = word0[:-22]

            # the others might be more than one
            words1 = words[1:]
            for tag_word1 in words1:
                if not tag_word1.has_attr("title"):
                    logg.debug(f"Missing title 1: {tag_word1}")
                    continue

                word1: str = tag_word1["title"]
                if word1.endswith(" (page does not exist)"):
                    word1 = word1[:-22]

                if word0 not in word_pairs:
                    word_pairs[word0] = [word1]
                else:
                    # do not add duplicates for the same word
                    if word1 not in word_pairs[word0]:
                        word_pairs[word0].append(word1)

        # save the output
        with pairs_path.open("w", encoding="utf-8") as jsonfile:
            json.dump(word_pairs, jsonfile, ensure_ascii=False, indent=2)


def run_download_wikitionary(args: argparse.Namespace) -> None:
    r"""Download and parse the wikitionary to extract word pairs.

    Args:
        args: The parsed cmdline arguments.
    """
    logg = logging.getLogger(f"c.{__name__}.run_download_wikitionary")
    logg.setLevel("DEBUG")
    logg.debug("Starting run_download_wikitionary")

    download_pages()

    parse_pages()


if __name__ == "__main__":
    args = setup_env()
    run_download_wikitionary(args)
