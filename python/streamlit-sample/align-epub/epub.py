"""Class to load an EPub in memory and analyze it.

Split in chapter, paragraph, sentences.

Sentences are translated.
"""
import re
import zipfile
from collections import Counter
from pathlib import Path
from typing import IO, Union

from bs4 import BeautifulSoup, Tag  # type:ignore
from spacy.language import Language  # type: ignore

from cached_pipe import TranslationPipelineCache

VALID_CHAP_EXT = [".xhtml", ".xml", ".html"]


class Paragraph:
    """Paragraph class."""

    def __init__(
        self,
        p_tag: Tag,
        chapter: "Chapter",
    ) -> None:
        """Initialize a paragraph.

        TODO:
            Filter sentences that are too short?
                No: do not split in sentences if the par is short.
        """
        self.chapter = chapter

        self.nlp: dict[str, Language] = self.chapter.nlp
        self.pipe: dict[str, TranslationPipelineCache] = self.chapter.pipe
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
    """Chapter class."""

    def __init__(
        self,
        chap_content: bytes,
        chap_file_name: str,
        epub: "EPub",
    ) -> None:
        """Initialize a chapter.

        TODO:
            Pass lang tags?
            Pass reference to EPub?
        """
        self.chap_file_name = chap_file_name
        self.epub = epub

        self.nlp: dict[str, Language] = self.epub.nlp
        self.pipe: dict[str, TranslationPipelineCache] = self.epub.pipe
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
        for p_tag in self.all_p_tag[:]:
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

    def enumerate_sents(
        self,
        start_par: int = 0,
        end_par: int = 0,
        which_sent="orig",
    ):
        """Enumerate all the sentences in the chapter, indexed as (par_id, sent_id)."""
        if end_par == 0:
            end_par = len(self.paragraphs) + 1
        for i_p, par in enumerate(self.paragraphs[start_par:end_par]):
            for i_s, sent in enumerate(par.sents_orig):
                if which_sent == "orig":
                    yield (i_p + start_par, i_s), sent
                elif which_sent == "tran":
                    yield (i_p + start_par, i_s), par.sents_tran[i_s]


class EPub:
    """EPub class."""

    def __init__(
        self,
        zipped_file: Union[str, IO[bytes], Path],
        nlp: dict[str, Language],
        pipe: dict[str, TranslationPipelineCache],
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
        self.input_zip = zipfile.ZipFile(self.zipped_file)

        # analyze the contents and find the chapter file names
        self.zipped_file_paths = [Path(p) for p in self.input_zip.namelist()]
        self.get_text_chapters()
        self.chap_file_names = [str(p) for p in self.chap_file_paths]

        # build a list of chapters
        # self.chapters = [
        #     Chapter(self.input_zip.read(chap_file_name), chap_file_name, self.nlp)
        #     for chap_file_name in self.chap_file_names
        # ]
        self.chapters: list[Chapter] = []
        for chap_file_name in self.chap_file_names[:6]:
            self.chapters.append(
                Chapter(
                    self.input_zip.read(chap_file_name),
                    chap_file_name,
                    self,
                )
            )

    def get_text_chapters(self) -> None:
        """Find the chapters names that match a regex ``name{number}`` and sort on ``number``."""
        # get the paths that are valid xhtml and similar
        self.chap_file_paths = [
            f for f in self.zipped_file_paths if f.suffix in VALID_CHAP_EXT
        ]

        # stem gets the file name without extensions
        stems = [f.stem for f in self.chap_file_paths]

        # get the longest stem
        max_stem_len = max(len(c) for c in stems)

        # track the best regex' performances
        best_match_num = 0
        best_stem_re = re.compile("")

        # iterate over the len, looking for the best match
        for num_kept_chars in range(max_stem_len):

            # keep only the beginning of the names
            stem_chops = [s[:num_kept_chars] for s in stems]

            # count how many names have common prefix
            stem_freqs = Counter(stem_chops)

            # if there are no chapters with common prefix skip
            if stem_freqs.most_common()[0][1] == 1:
                continue

            # try to match the prefix with re
            for stem_might, stem_freq in stem_freqs.items():

                # compile a regex looking for name{number}
                stem_re = re.compile(f"{stem_might}(\\d+)")

                # how many matches this stem has
                good_match_num = 0

                # track if a regex fails: it can have some matches and then fail
                failed = False

                for stem in stems:
                    stem_ch = stem[:num_kept_chars]
                    match = stem_re.match(stem)

                    # if the regex does not match but the stem prefix does, fails
                    if match is None and stem_ch == stem_might:
                        failed = True
                        break

                    good_match_num += 1

                # if this stem failed to match, don't consider it for the best
                if failed:
                    continue

                # update info on best matching regex
                if good_match_num > best_match_num:
                    best_stem_re = stem_re
                    best_match_num = good_match_num

        # if the best match sucks keep all chapters
        if best_match_num <= 2:
            return

        # pair chapter name and chapter number
        chap_file_paths_id: list[tuple[Path, int]] = []
        for stem, chap_file_path in zip(stems, self.chap_file_paths):

            # match the stem and get the chapter number
            match = best_stem_re.match(stem)
            if match is None:
                continue
            chap_id = int(match.group(1))
            chap_file_paths_id.append((chap_file_path, chap_id))

        # sort the list according to the extracted id
        self.chap_file_paths = [
            cid[0] for cid in sorted(chap_file_paths_id, key=lambda x: x[1])
        ]

    def get_chapter_by_name(self, chap_file_name: str) -> Chapter:
        """Get the chapter with the requested name."""
        chap_id = self.chap_file_names.index(chap_file_name)
        print(chap_id)
        return self.chapters[chap_id]
