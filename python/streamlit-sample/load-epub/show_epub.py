"""Show an epub."""
import re
from collections import Counter
from pathlib import Path
from typing import IO, cast
from zipfile import ZipFile

import streamlit as st
from bs4 import BeautifulSoup  # type: ignore

VALID_EBOOK_EXT = [".epub"]
VALID_CHAP_EXT = [".xhtml", ".xml", ".html"]


def get_text_chapters(chap_file_paths: list[Path]) -> list[Path]:
    """Find the chapters names that match a regex ``name{number}`` and return them sorted on ``number``."""

    # stem gets the file name without extensions
    stems = [f.stem for f in chap_file_paths]

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
            stem_re = re.compile(f"{stem_might}(\d+)")

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

    # if the best match sucks return all chapters
    if best_match_num <= 2:
        return chap_file_paths

    # pair chapter name and chapter number
    chap_file_paths_id: list[tuple[Path, int]] = []
    for stem, chap_file_path in zip(stems, chap_file_paths):

        # match the stem and get the chapter number
        match = best_stem_re.match(stem)
        if match is None:
            continue
        chap_id = int(match.group(1))
        chap_file_paths_id.append((chap_file_path, chap_id))

    # sort the list according to the extracted id
    chap_file_paths = [cid[0] for cid in sorted(chap_file_paths_id, key=lambda x: x[1])]

    return chap_file_paths


def main() -> None:
    """Load and show an EPub."""

    # a silly title, will be substituted with the actual chapter title
    title = st.title("Load and show an epub")
    st.sidebar.title("Load and show an epub")

    # load the translator model
    # translator = load_translator()

    # load a file in the app
    epub_file = cast(
        IO[bytes], st.sidebar.file_uploader("Choose a file:", type=VALID_EBOOK_EXT)
    )

    # wait for a file to be loaded
    if epub_file is None:
        st.write("Drop a file in the sidebar!")
        return

    # read it in memory
    input_zip = ZipFile(epub_file)

    # get the file list, use Path because we need the suffixex
    zipped_file_paths = sorted([Path(p) for p in input_zip.namelist()])

    # filter chapters that are not valid text chaps
    chap_file_paths = [f for f in zipped_file_paths if f.suffix in VALID_CHAP_EXT]

    # clean up more and sort properly
    # TODO: some way to disable this if it fails horribly
    chap_file_paths = get_text_chapters(chap_file_paths)

    # the chapters paths as strings to show them in the selectbox
    # TODO: which is a horrible hack as we lose them being Path
    # only because zip.read() accepts strings as well, but I don't like it
    chap_file_path_strings = [str(p) for p in chap_file_paths]

    # pick the chapter from the sidebar
    chap_file_name = st.sidebar.selectbox("Pick a chapter:", chap_file_path_strings)
    title.title(f"{chap_file_name}")

    # TODO add buttons to change chapter

    # load the raw chapter content
    ch_content_bytes = input_zip.read(chap_file_name)

    # parse it as soup and get the body
    soup = BeautifulSoup(ch_content_bytes, features="html.parser")
    body = soup.body
    if body is None:
        st.write("No body found in the chapter")
        return

    # find all paragraph
    all_p = body.find_all("p")
    if len(all_p) == 0:
        st.write("No paragraphs found in the chapter, try to select another one.")
        return

    # split each paragraph in sentences, and translate them
    for i, par in enumerate(all_p):

        # get all the text in the paragraph
        par_str = par.getText(strip=True)
        print(f"\n\n{i} {par_str}")

        st.write(par_str)

        # # split the paragraph in sentences
        # split_par_list = split_par(par_str)

        # # show them
        # for orig in zip(split_par_list):
        #     col1, col2 = st.columns(1)
        #     col1.write(orig)
        #     col2.write(tran)

        # if i > 5: break


if __name__ == "__main__":
    main()
