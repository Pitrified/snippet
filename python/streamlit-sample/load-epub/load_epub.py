"""Load an epub and extract the chapters.

https://stackoverflow.com/questions/10908877/extracting-a-zipfile-to-memory
"""
from pathlib import Path
import re
from timeit import default_timer as timer
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

# task = "en_to_fr"
# translator = {task: pipeline("translation_en_to_fr")}


# def sad_hash(t): return 0


# @st.cache(hash_funcs={tokenizers.Tokenizer: sad_hash})
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

    title = st.title("Load and show an epub")
    st.sidebar.title("Load and show an epub")

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
    zipped_file_paths = [Path(p) for p in input_zip.namelist()]

    # filter some non-text chapter
    chap_file_paths = [
        f
        for f in zipped_file_paths
        if f.suffix in VALID_CHAP_EXT and "META-INF" not in str(f)
    ]

    # chap_file_names = [p.stem for p in chap_file_paths]
    chap_file_names = [str(p) for p in chap_file_paths]

    # pick the chapter from the sidebar
    ch_file_name = st.sidebar.selectbox("Pick a chapter:", chap_file_names)
    title.title(f"{ch_file_name}")

    # load the raw chapter content
    ch_content_bytes = input_zip.read(ch_file_name)

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

    for i, par in enumerate(all_p):
        par_str = par.string
        st.write(f"{i} {par_str}")
        st.write(re.split("\\.|!|\\?", par_str))
        if i > 5:
            break

    t_start_load = timer()
    translator = load_translator()
    t_end_load = timer()

    # translated = translate(translator, "How old are you?")[0]["translation_text"]
    # st.write(translated)

    st.write(f"Loaded {type(translator)=}")
    st.write(f"Loading took {t_end_load-t_start_load} s")

    translated = translate(
        translator,
        [
            "How old are you?",
            "How are you?",
            "What is the difference between good and evil?",
            "Is this the real life?",
        ],
    )
    t_end_translate = timer()
    st.write(translated)

    st.write(f"Translating took {t_end_translate-t_end_load} s")


if __name__ == "__main__":
    main()
