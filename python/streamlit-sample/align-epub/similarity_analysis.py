"""Analyze the similarity of sentences."""
from pathlib import Path
from typing import IO, Optional, cast

import spacy
import streamlit as st
import tokenizers  # type: ignore
import torch
import transformers
from matplotlib import pyplot as plt
from sentence_transformers import SentenceTransformer, util  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity
from thinc.model import Model
from transformers.pipelines import pipeline
from transformers.pipelines.text2text_generation import TranslationPipeline

from cached_pipe import TranslationPipelineCache
from epub import EPub
from utils import sentence_encode_np, spacy_load_cached

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
    TranslationPipelineCache,
]
UNHASH_FUNC = {t: lambda x: 0 for t in UNHASHABLE_TYPES}


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_translator(
    lts_pair, load_pipeline
) -> dict[str, Optional[TranslationPipeline]]:
    """Load the translator pipelines."""
    pipe = {
        f"{lt}_{lt_other}": cast(
            TranslationPipeline,
            pipeline("translation", model=f"Helsinki-NLP/opus-mt-{lt}-{lt_other}"),
        )
        if load_pipeline[lt]
        else None
        for lt, lt_other in lts_pair
    }
    return pipe


@st.cache(hash_funcs=UNHASH_FUNC, allow_output_mutation=True)
def load_nlp_spacy():
    """Load the spacy models."""
    cache_dir = Path("~/.cache/spacy_my_models").expanduser()
    nlp = {
        "en": spacy_load_cached("en_core_web_md", cache_dir),
        "fr": spacy_load_cached("fr_core_news_md", cache_dir),
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
    load_pipeline = {
        "en": False,
        # "fr": True,
        "fr": False,
    }
    pipe = load_translator(lts_pair, load_pipeline)
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

    # load the epubs
    epub = load_epubs(lts_pair, pipe_cache, nlp, epub_file)
    text.text("Done loading EPubs!")

    # add selectors for chapters
    chap_selectbox = {
        lt: side_cont[lt].selectbox(
            "Pick a chapter:", epub[lt].chap_file_names, key=f"selectbox_{lt}"
        )
        for lt in lts
    }

    # get the right chapter name
    chap_selected_name = {lt: chap_selectbox[lt] for lt in lts}
    st.write(f"{chap_selected_name}")

    # get the chapter
    chap_selected = {lt: epub[lt].get_chapter_by_name(chap_selectbox[lt]) for lt in lts}
    st.write(f"{chap_selected}")

    # print some sentence to see something
    sent_fr = chap_selected["fr"].paragraphs[0].sents_orig[0]
    st.write(f"{sent_fr.text=}")
    sent_en = chap_selected["en"].paragraphs[0].sents_orig[0]
    st.write(f"{sent_en.text=}")
    if pipe["fr_en"] is not None:
        sent_fr_to_en = pipe["fr_en"](sent_fr.text)
        st.write(f'{sent_fr_to_en[0]["translation_text"]=}')

    # # TODO chapter number picker
    # # TODO chapter delta fixer
    # ch_index = {lt: 0 for lt in lts}
    # ch_delta = 0
    # epub["en"].chapters[ch_index["en"] + ch_delta]

    # all sentences at once
    sents_text_en_orig = []
    for k, sent in chap_selected["en"].enumerate_sents(which_sent="orig"):
        text_en = sent.text
        sents_text_en_orig.append(text_en)
    sents_text_fr_tran = []
    for k, sent in chap_selected["fr"].enumerate_sents(which_sent="tran"):
        text_fr_tran = sent.text
        sents_text_fr_tran.append(text_fr_tran)
    sents_text_fr_orig = []
    for k, sent in chap_selected["fr"].enumerate_sents(which_sent="orig"):
        text_fr_orig = sent.text
        sents_text_fr_orig.append(text_fr_orig)
    sents_num_en = len(sents_text_en_orig)
    sents_num_fr = len(sents_text_fr_tran)
    st.write(f"{sents_text_en_orig[0]=}")
    st.write(f"{sents_text_fr_tran[0]=}")
    st.write(f"{sents_text_fr_orig[0]=}")

    # encode them
    enc_en_orig = sentence_encode_np(sent_transformer["en"], sents_text_en_orig)
    enc_fr_tran = sentence_encode_np(sent_transformer["en"], sents_text_fr_tran)
    st.write("en", enc_en_orig.shape, sents_num_en, enc_en_orig[0].shape)
    st.write("fr", enc_fr_tran.shape, sents_num_fr, enc_fr_tran[0].shape)

    # compute the similarity
    sim = cosine_similarity(enc_en_orig, enc_fr_tran)
    fig, ax = plt.subplots()
    ax.imshow(sim)
    ax.set_title(f"Similarity *en* vs *fr_translated*")
    ax.set_ylabel("en")
    ax.set_xlabel("fr_tran")
    st.pyplot(fig)

    text.text("Done computing similarity!")

    # show sentences to understand what is happening

    # show them
    for sent_en_orig, sent_fr_tran, sent_fr_orig in zip(
        sents_text_en_orig, sents_text_fr_tran, sents_text_fr_orig
    ):
        col1, col2, col3 = st.columns(3)
        col1.write(sent_en_orig)
        col2.write(sent_fr_tran)
        col3.write(sent_fr_orig)
    # if i > 5: break


if __name__ == "__main__":
    main()
