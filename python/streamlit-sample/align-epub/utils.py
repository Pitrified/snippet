from pathlib import Path

from epub import (
    EPub,
    Chapter,
)


def get_ebook_folder():
    """Get the folder holding the books in the snippet repo."""

    this_file = Path(__file__).absolute()
    snippet_folder = this_file.parent.parent.parent.parent
    ebook_folder = snippet_folder / "datasets" / "ebook"
    return ebook_folder


def enumerate_sent(
    chap: Chapter,
    start_par: int = 0,
    end_par: int = 0,
    which_sent="orig",
):
    """Enumerate all the sentences in a chapter, indexed as (par_id, sent_id)."""
    if end_par == 0:
        end_par = len(chap.paragraphs) + 1
    for i_p, par in enumerate(chap.paragraphs[start_par:end_par]):
        for i_s, sent in enumerate(par.sents_orig):
            if which_sent == "orig":
                yield (i_p + start_par, i_s), sent
            elif which_sent == "tran":
                yield (i_p + start_par, i_s), par.sents_tran[i_s]
