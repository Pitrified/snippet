from __future__ import annotations

from pathlib import Path
from typing import IO, Union
import zipfile

from bs4 import BeautifulSoup, Tag  # type:ignore
from spacy.language import Language  # type: ignore

from cached_pipe import PipelineCache

VALID_CHAP_EXT = [".xhtml", ".xml", ".html"]


class Paragraph:
    def __init__(
        self,
        p_tag: Tag,
        chapter: Chapter,
    ) -> None:
        """Initialize a paragraph.

        TODO:
            Some clean up of the text? Eg remove \\n.
            Filter sentences that are too short?
        """

        self.chapter = chapter

        self.nlp: dict[str, Language] = self.chapter.nlp
        self.pipe: dict[str, PipelineCache] = self.chapter.pipe
        self.lang_orig: str = self.chapter.lang_orig
        self.lang_dest: str = self.chapter.lang_dest

        self.lang_tr = f"{self.lang_orig}_{self.lang_dest}"

        self.p_tag = p_tag

        # MAYBE: move to method that does clean up well
        self.par_str = str(self.p_tag.string)  # we want a str, not a NavigableString
        self.par_str = self.par_str.replace("\n\r", " ")
        self.par_str = self.par_str.replace("\n", " ")
        self.par_str = self.par_str.replace("\r", " ")

        self.par_doc = self.nlp[self.lang_orig](self.par_str)
        self.sents_orig = list(self.par_doc.sents)

        self.sents_tran = []
        for sent in self.sents_orig:
            str_tran = self.pipe[self.lang_tr](sent.text)
            # sent_tran = self.nlp[self.lang_dest](str_tran[0]["translation_text"])
            sent_tran = self.nlp[self.lang_dest](str_tran)
            self.sents_tran.append(sent_tran)


class Chapter:
    def __init__(
        self,
        chap_content: bytes,
        chap_file_name: str,
        epub: EPub,
    ) -> None:
        """Initialize a chapter.

        TODO:
            Pass lang tags?
            Pass reference to EPub?
        """

        self.chap_file_name = chap_file_name
        self.epub = epub

        self.nlp: dict[str, Language] = self.epub.nlp
        self.pipe: dict[str, PipelineCache] = self.epub.pipe
        self.lang_orig: str = self.epub.lang_orig
        self.lang_dest: str = self.epub.lang_dest

        # parse the soup and get the body
        self.soup = BeautifulSoup(chap_content, features="html.parser")
        self.body = self.soup.body
        if self.body is None:
            print(f"No body found in chapter {self.chap_file_name} of book {'book'}.")
            return

        # find the paragraphs
        self.all_p_tag = self.body.find_all("p")
        if len(self.all_p_tag) == 0:
            print(
                f"No paragraphs found in chapter {self.chap_file_name} of book {'book'}."
            )
            return

        # build the list of Paragraphs
        # self.paragraphs = [Paragraph(p_tag, self.nlp) for p_tag in self.all_p_tag]
        self.paragraphs = []
        for p_tag in self.all_p_tag[:15]:
            self.paragraphs.append(Paragraph(p_tag, self))

        self.build_index()

    def build_index(self):
        """Build maps to go from ``sent_in_chap_id`` to ``(par_id, sent_in_par_id)`` and vice-versa."""
        self.parsent_to_sent = {}
        self.sent_to_parsent = {}
        sc_id = 0
        for p_id, par in enumerate(self.paragraphs):
            for sp_id, sent in enumerate(par.sents_orig):
                self.parsent_to_sent[(p_id, sp_id)] = sc_id
                self.sent_to_parsent[sc_id] = (p_id, sp_id)
                sc_id += 1


class EPub:
    def __init__(
        self,
        zipped_file: Union[str, IO[bytes]],
        nlp: dict[str, Language],
        pipe: dict[str, PipelineCache],
        lang_orig: str,
        lang_dest: str,
    ) -> None:
        """Initialize an epub.

        TODO:
            Pass file name? Yes, better debug. No can do with streamlit...
                But I'd rather pass a fake name inside streamlit,
                and the real one usually.
        """

        self.nlp = nlp
        self.pipe = pipe
        self.lang_orig = lang_orig
        self.lang_dest = lang_dest

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
        # self.chapters = [
        #     Chapter(self.input_zip.read(chap_file_name), chap_file_name, self.nlp)
        #     for chap_file_name in self.chap_file_names
        # ]
        self.chapters = []
        for chap_file_name in self.chap_file_names[:3]:
            self.chapters.append(
                Chapter(
                    self.input_zip.read(chap_file_name),
                    chap_file_name,
                    self,
                )
            )
