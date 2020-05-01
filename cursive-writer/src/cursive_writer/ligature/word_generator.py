import logging
import numpy as np  # type: ignore
import string

from random import randint

from cursive_writer.utils.setup import setup_logger

from typing import Iterable, List
from pathlib import Path


def load_words(word_file: Path) -> List[str]:
    valid_words = word_file.read_text().split()
    return valid_words


def generate_word(let_available: Iterable[str], word_file: Path) -> str:
    """TODO: what is generate_word doing?
    """
    logg = logging.getLogger(f"c.{__name__}.generate_word")
    logg.debug(f"Start generate_word available {let_available}")

    valid_words = load_words(word_file)
    tot_words = len(valid_words)
    logg.debug(f"tot_words: {tot_words}")

    word_by_letter = np.zeros((tot_words, 26), dtype=bool)

    let_index = {l: i for i, l in enumerate(string.ascii_lowercase)}
    # logg.debug(f"let_index: {let_index}")

    # for each word, set the columns corresponding to the letters in it to True
    for i_w, word in enumerate(valid_words):
        for letter in set(word):
            word_by_letter[i_w][let_index[letter]] = True

    # for each available letter, set the entire column to false
    for letter in let_available:
        i_l = let_index[letter]
        word_by_letter[:, i_l] = False

    # the words that are all false are only made by character in let_available
    all_seen = np.max(word_by_letter, axis=1)

    # select the word indexes that are relative to all false words
    word_index = np.arange(tot_words)
    seen_index = word_index[~all_seen]
    # logg.debug(f"seen_index: {seen_index}")
    # logg.debug(f"seen_index.shape: {seen_index.shape}")

    # pick a random index from one of them
    rand_index = seen_index[randint(0, seen_index.shape[0] - 1)]
    # logg.debug(f"rand_index: {rand_index}")

    # get the word associated
    the_word = valid_words[rand_index]
    # logg.debug(f"the_word: {the_word}")

    # for w_i in seen_index: logg.debug(f"valid_words[{w_i}]: {valid_words[w_i]}")

    return the_word


def test_generator():
    """TODO: what is test_generator doing?
    """
    logg = logging.getLogger(f"c.{__name__}.test_generator")
    logg.debug(f"Start test_generator")

    main_dir = Path(__file__).resolve().parent
    data_dir = main_dir.parent / "data"
    word_file = data_dir / "wordlist" / "3of6game_filt.txt"
    logg.debug(f"word_file: {word_file}")

    # let_available = "abcd"
    # let_available = "abcdefgh"
    # let_available = "imnpuv"
    let_available = "cmseihgr"
    input_str = generate_word(let_available, word_file)
    logg.debug(f"input_str: {input_str}")


if __name__ == "__main__":
    setup_logger("DEBUG", "m")
    test_generator()
