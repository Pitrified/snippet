from bdb import effective
from pathlib import Path


def get_ebook_folder():

    this_file = Path(__file__).absolute()
    snippet_folder = this_file.parent.parent.parent.parent
    ebook_folder = snippet_folder / "datasets" / "ebook"
    return ebook_folder
