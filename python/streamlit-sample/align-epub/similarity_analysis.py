"""Analyze the similarity of sentences."""
from pathlib import Path
from typing import IO, cast

import spacy
import streamlit as st
import tokenizers  # type: ignore
import torch
import transformers
from sentence_transformers import SentenceTransformer, util  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity
from thinc.model import Model
from transformers.pipelines import pipeline
from transformers.pipelines.text2text_generation import TranslationPipeline

from cached_pipe import TranslationPipelineCache
from epub import EPub
from utils import enumerate_sent, sentence_encode_np

VALID_EBOOK_EXT = [".epub"]
UNHASHABLE_TYPES = [
    EPub,
    SentenceTransformer,
    spacy.language.Language,
    spacy.vocab.Vocab,
    spacy.pipeline.tok2vec.Tok2Vec,
    # thinc.model.Model,
    Model,
    tokenizers.Tokenizer,
    torch.nn.parameter.Parameter,
    transformers.pipelines.text2text_generation.TranslationPipeline,
]
UNHASH_FUNC = {t: lambda x: 0 for t in UNHASHABLE_TYPES}


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_translator(lts_pair) -> dict[str, TranslationPipeline]:
    """Load the translator pipelines."""
    pipe = {
        f"{lt}_{lt_other}": cast(
            TranslationPipeline,
            pipeline("translation", model=f"Helsinki-NLP/opus-mt-{lt}-{lt_other}"),
        )
        for lt, lt_other in lts_pair
    }
    return pipe


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_nlp_spacy():
    """Load the spacy models."""
    nlp = {
        "en": spacy.load("en_core_web_md"),
        "fr": spacy.load("fr_core_news_md"),
    }
    return nlp


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_sent_transformer():
    """Load the sentence transformer."""
    st = {
        "en": SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"),
    }
    return st


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_epubs(lts_pair, pipe_cache, nlp, epub_file):
    """Load the EPubs."""
    epub = {
        lt: EPub(epub_file[lt], nlp, pipe_cache, lt, lt_other)
        for lt, lt_other in lts_pair
    }
    return epub


def main():
    """Run streamlit app."""
    text = st.sidebar.text("Starting!")

    # basic lang info and useful tags
    lts = ["en", "fr"]
    lts_pair = list(zip(lts, lts[::-1]))
    lt_to_lang_name = {"en": "English", "fr": "French"}

    # load huggingface magic
    pipe = load_translator(lts_pair)
    cache_file_path = {
        f"{lt}_{lt_other}": Path(f"translated_{lt}_{lt_other}.json")
        for lt, lt_other in lts_pair
    }
    pipe_cache = {
        (lt_pair := f"{lt}_{lt_other}"): TranslationPipelineCache(
            pipe[lt_pair], cache_file_path[lt_pair], lt, lt_other
        )
        for lt, lt_other in lts_pair
    }

    # load spacy magic
    nlp = load_nlp_spacy()

    # load more magic
    sent_transformer = load_sent_transformer()

    text.text("Done loading NLP magic!")

    # containers for elements in the sidebar
    side_cont = {lt: st.sidebar.container() for lt in lts}

    # headers
    head_side = {
        lt: side_cont[lt].title(f"Info for {lt_to_lang_name[lt]}:") for lt in lts
    }

    # load a file in the app
    epub_file = {
        lt: cast(
            IO[bytes],
            side_cont[lt].file_uploader(
                f"Choose a file for {lt_to_lang_name[lt]}:",
                type=VALID_EBOOK_EXT,
                key=f"lang_{lt}",
            ),
        )
        for lt in lts
    }

    # wait for both files to be loaded
    if any(epub_file[lt] is None for lt in lts):
        st.write("Drop two files in the sidebar!")
        return

    epub = load_epubs(lts_pair, pipe_cache, nlp, epub_file)

    text.text("Done loading EPubs!")

    sent_fr = epub["fr"].chapters[0].paragraphs[0].sents_orig[0]
    st.write(sent_fr.text)

    sent_fr_to_en = pipe["fr_en"](sent_fr.text)
    st.write(sent_fr_to_en[0]["translation_text"])

    # TODO chapter number picker
    # TODO chapter delta fixer
    ch_index = {lt: 0 for lt in lts}
    ch_delta = 2

    # all sentences at once
    sent_text_en = []
    for k, sent in enumerate_sent(
        epub["en"].chapters[ch_index["en"] + ch_delta], which_sent="orig"
    ):
        text_en = sent.text
        sent_text_en.append(text_en)
    sent_text_fr_tran = []
    for k, sent in enumerate_sent(
        epub["fr"].chapters[ch_index["fr"]], which_sent="tran"
    ):
        text_fr_tran = sent.text
        sent_text_fr_tran.append(text_fr_tran)
    sent_num_en = len(sent_text_en)
    sent_num_fr = len(sent_text_fr_tran)
    st.write(sent_text_en[0])
    st.write(sent_text_fr_tran[0])

    # encode them
    # enc_en = sent_transformer["en"].encode(sent_text_en, convert_to_tensor=True)
    # enc_fr_tran = sent_transformer["en"].encode(
    #     sent_text_fr_tran, convert_to_tensor=True
    # )
    enc_en = sentence_encode_np(sent_transformer["en"], sent_text_en)
    enc_fr_tran = sentence_encode_np(sent_transformer["en"], sent_text_fr_tran)

    st.write("en", enc_en.shape, sent_num_en, enc_en[0].shape)
    st.write("fr", enc_fr_tran.shape, sent_num_fr, enc_fr_tran[0].shape)

    sim = cosine_similarity(enc_en, enc_fr_tran)

    text.text("Done computing similarity!")


if __name__ == "__main__":
    main()
