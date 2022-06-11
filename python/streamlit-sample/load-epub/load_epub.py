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
    # model_checkpoint = "Helsinki-NLP/opus-mt-en-fr"
    model_checkpoint = "Helsinki-NLP/opus-mt-fr-en"
    return pipeline("translation", model=model_checkpoint)


# @st.cache(hash_funcs={tokenizers.Tokenizer: sad_hash})
@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def translate(translator, sentence):
    return translator(sentence)


def split_par(
    par: str,
    min_sentence_len: int = 10,
    max_sentence_len: int = 100,
) -> list[str]:
    sentences = re.split("(\\.|!|\\?)", par)
    sentences = [s.strip() for s in sentences]
    i = 0
    while i < len(sentences) - 1:
        # if the current sentence is short
        # or the next is punctiation
        # or the next is short and the current is also not super long
        # or the next is a »
        curr_sent_len = sentences[i].count(" ")
        next_sent_len = sentences[i + 1].count(" ")
        if (
            curr_sent_len < min_sentence_len
            or len(sentences[i + 1]) == 1
            or (next_sent_len < min_sentence_len and curr_sent_len < max_sentence_len)
            or sentences[i + 1][0] == "»"
            or sentences[i].endswith("M.")
        ):
            # decide if we need a space between sentences, not needed for punctuation
            space = " " if len(sentences[i + 1]) > 1 else ""
            # merge i on the next
            sentences[i + 1] = sentences[i] + space + sentences[i + 1]
            # there cannot be another sentence like [i] before [i],
            # as it would have been merged
            sentences.remove(sentences[i])
            # the list is now shorter
            i -= 1
        i += 1

    # if the paragraph ends with punctiation, there is an empty last sentence
    if len(sentences) > 0 and sentences[-1] == "":
        sentences = sentences[:-1]

    return sentences


def main():

    title = st.title("Load and show an epub")
    st.sidebar.title("Load and show an epub")

    # load the translator model
    translator = load_translator()

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

    translate_start = timer()
    # split each paragraph in sentences, and translate them
    for i, par in enumerate(all_p):
        # st.write(f"------ {i} {par}")
        par_str = par.getText()
        # st.write(f"------ {i} {par_str}")

        split_par_list = split_par(par_str)
        translated = translate(translator, split_par_list)
        translated = [t["translation_text"] for t in translated]

        # st.write(list(zip(split_par_list, translated)))
        for orig, tran in zip(split_par_list, translated):
            col1, col2 = st.columns(2)
            col1.write(orig)
            col2.write(tran)

        # if i > 5: break

    translate_end = timer()
    st.write(f"Translating took {translate_end-translate_start:.0f}s")


if __name__ == "__main__":
    main()
