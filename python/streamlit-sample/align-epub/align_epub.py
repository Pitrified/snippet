"""Align a chapter sentence by sentence."""

from itertools import zip_longest
from pathlib import Path
from timeit import default_timer as timer
from turtle import end_fill
from typing import (
    cast,
    IO,
)
from zipfile import ZipFile

from bs4 import BeautifulSoup  # type: ignore
import tokenizers  # type: ignore
from transformers import pipeline
import streamlit as st
import torch

VALID_EBOOK_EXT = [".epub"]
VALID_CHAP_EXT = [".xhtml", ".xml", ".html"]
UNHASHABLE_TYPES = [
    torch.nn.parameter.Parameter,
    tokenizers.Tokenizer,
    # transformers.pipelines.text2text_generation.TranslationPipeline,
]
UNHASH_FUNC = {t: lambda x: 0 for t in UNHASHABLE_TYPES}


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_translator():
    # return pipeline("translation_en_to_fr", model_max_length=512)
    model_checkpoint = "Helsinki-NLP/opus-mt-en-fr"
    return pipeline("translation", model=model_checkpoint)


# @st.cache(hash_funcs={tokenizers.Tokenizer: sad_hash})
@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def translate(translator, sentence):
    return translator(sentence)


def main():
    """Main function of the aligner."""

    # wide layout
    st.set_page_config(layout="wide")

    title = st.title("Load and align two epub books")

    # # load the translator model
    # translator = load_translator()

    # language tags
    lts = ["en", "fr"]
    lt_to_lang_name = {
        "en": "English",
        "fr": "French",
    }

    # containers for elements in the sidebar
    side_cont = {lt: st.sidebar.container() for lt in lts}

    # headers
    head_side = {lt: side_cont[lt].title(f"Info for {lt_to_lang_name[lt]}:") for lt in lts}

    # load a file in the app
    epub_file = {
        lt: cast(
            IO[bytes],
            side_cont[lt].file_uploader(
                f"Choose a file for {lt_to_lang_name[lt]}:", type=VALID_EBOOK_EXT, key=f"lang_{lt}"
            ),
        )
        for lt in lts
    }

    # wait for both files to be loaded
    if any(epub_file[lt] is None for lt in lts):
        st.write("Drop two files in the sidebar!")
        return

    # read them in memory
    input_zip = {lt: ZipFile(epub_file[lt]) for lt in lts}

    # get the file lists, use Path because we need the suffixex
    zipped_file_paths = {lt: [Path(p) for p in input_zip[lt].namelist()] for lt in lts}

    # filter some non-text chapter
    chap_file_paths = {
        lt: [
            f
            for f in zipped_file_paths[lt]
            if f.suffix in VALID_CHAP_EXT and "META-INF" not in str(f)
        ]
        for lt in lts
    }
    chap_file_names = {lt: [str(p) for p in chap_file_paths[lt]] for lt in lts}

    # pick the chapter from the sidebar
    ch_file_name = {
        lt: side_cont[lt].selectbox(
            f"Pick a chapter for {lt_to_lang_name[lt]}:", chap_file_names[lt]
        )
        for lt in lts
    }
    st.write(f"{ch_file_name}")

    # load the raw chapter content
    ch_content_bytes = {lt: input_zip[lt].read(ch_file_name[lt]) for lt in lts}

    # parse it as soup and get the body
    soup = {lt: BeautifulSoup(ch_content_bytes[lt], features="html.parser") for lt in lts}
    body = {lt: soup[lt].body for lt in lts}
    for lt in lts:
        if body[lt] is None:
            st.write(f"No body found in the chapter for {lt_to_lang_name[lt]}.")
            return

    # find all paragraph
    all_p = {lt: body[lt].find_all("p") for lt in lts}
    for lt in lts:
        if len(all_p[lt]) == 0:
            st.write(
                f"No paragraphs found in the chapter for {lt_to_lang_name[lt]},"
                " try to select another one."
            )
            return

    # st.write(list(all_p.values()))
    # st.write(all_p.values())

    # for p1, p2 in zip_longest(*all_p.values(), fillvalue="-"):
    for p1, p2 in zip_longest(*all_p.values()):
        # print(f"\n{p1.string=}\n{p2.string=}")
        c1, c2 = st.columns(2)
        if p1 is not None:
            c1.write(p1.string)
        else:
            c1.write("-")
        if p2 is not None:
            c2.write(p2.string)
        else:
            c1.write("-")


if __name__ == "__main__":
    main()
