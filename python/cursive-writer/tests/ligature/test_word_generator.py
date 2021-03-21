# import pytest  # type: ignore

from cursive_writer.ligature.word_generator import generate_word  # type: ignore
from pathlib import Path


def test_generate_word():
    main_dir = Path(__file__).resolve().parent
    data_dir = main_dir.parent.parent / "src" / "cursive_writer" / "data"
    word_file = data_dir / "wordlist" / "3of6game_filt.txt"
    let_available = "abcd"
    word = generate_word(let_available, word_file)
    for ch in word:
        assert ch in let_available
