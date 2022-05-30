from pathlib import Path
from typing import IO, Union
import zipfile

from bs4 import BeautifulSoup, Tag  # type:ignore
import spacy  # type: ignore

VALID_CHAP_EXT = [".xhtml", ".xml", ".html"]


class Paragraph:
    def __init__(self, p_tag: Tag, nlp: spacy.language.Language) -> None:
        """Initialize a paragraph."""

        self.nlp = nlp

        self.p_tag = p_tag
        self.par_str = str(self.p_tag.string)  # we want a str, not a NavigableString
        self.par_doc = self.nlp(self.par_str)
        self.sentences = list(self.par_doc.sents)


class Chapter:
    def __init__(
        self, chap_content: bytes, chap_file_name: str, nlp: spacy.language.Language
    ) -> None:
        """Initialize a chapter.

        TODO:
            Pass lang tags?
            Pass reference to EPub?
        """

        self.chap_file_name = chap_file_name
        self.nlp = nlp

        # parse the soup and get the body
        self.soup = BeautifulSoup(chap_content, features="html.parser")
        self.body = self.soup.body
        if self.body is None:
            print(f"No body found in chapter {self.chap_file_name} of book {'book'}.")
            return

        # load the paragraphs
        self.all_p_tag = self.body.find_all("p")
        if len(self.all_p_tag) == 0:
            print(f"No paragraphs found in chapter {self.chap_file_name} of book {'book'}.")
            return

        # build the list of sentences
        self.paragraphs = [Paragraph(p_tag, self.nlp) for p_tag in self.all_p_tag]


class EPub:
    def __init__(self, zipped_file: Union[str, IO[bytes]], nlp: spacy.language.Language) -> None:
        """Initialize an epub.

        TODO:
            Pass lang tags?
            Pass file name?
        """

        self.nlp = nlp

        # load the file in memory
        self.zipped_file = zipped_file
        self.input_zip = zipfile.ZipFile(zipped_file)

        # analyze the contents and find the chapter file names
        self.zipped_file_paths = [Path(p) for p in self.input_zip.namelist()]
        self.chap_file_paths = [
            f
            for f in self.zipped_file_paths
            if f.suffix in VALID_CHAP_EXT and "META-INF" not in str(f)
        ]
        self.chap_file_names = [str(p) for p in self.chap_file_paths]

        # build a list of chapters
        self.chapters = [
            Chapter(self.input_zip.read(chap_file_name), chap_file_name, self.nlp)
            for chap_file_name in self.chap_file_names
        ]
