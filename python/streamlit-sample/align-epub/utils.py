"""Utils to deal with with ebooks."""
import re
from collections import Counter
from pathlib import Path
from typing import cast

import numpy as np
import spacy
import streamlit as st
from matplotlib import pyplot as plt
from scipy.signal.windows import triang
from sentence_transformers import SentenceTransformer, util
from torch import Tensor

from epub import Chapter, EPub


def get_ebook_folder():
    """Get the folder holding the books in the snippet repo."""
    this_file = Path(__file__).absolute()
    snippet_folder = this_file.parent.parent.parent.parent
    ebook_folder = snippet_folder / "datasets" / "ebook"
    return ebook_folder


def enumerate_sent(
    chap: Chapter,
    start_par: int = 0,
    end_par: int = 0,
    which_sent="orig",
):
    """Enumerate all the sentences in a chapter, indexed as (par_id, sent_id)."""
    if end_par == 0:
        end_par = len(chap.paragraphs) + 1
    for i_p, par in enumerate(chap.paragraphs[start_par:end_par]):
        for i_s, sent in enumerate(par.sents_orig):
            if which_sent == "orig":
                yield (i_p + start_par, i_s), sent
            elif which_sent == "tran":
                yield (i_p + start_par, i_s), par.sents_tran[i_s]


def spacy_load_cached(model_path: str, cache_dir: Path) -> spacy.language.Language:
    """Load cached spacy models from a single location.

    https://stackoverflow.com/a/67750919

    Args:
        model_path (str): Name of the model, compatible with
            ``nlp = spacy.load(model_path)``.
        cache_dir (Path): Folder to search the models in.

    Returns:
        spacy.language.Language: Loaded model.
    """
    if not cache_dir.exists():
        Path.mkdir(cache_dir, parents=True)

    try:
        # try to load from cache
        nlp = spacy.load(cache_dir / model_path)
    except OSError:
        # load with spacy.load
        nlp = spacy.load(model_path)
        # save to disk
        nlp.to_disk(cache_dir / model_path)

    return nlp


def sentence_encode_np(
    sentence_transformer: SentenceTransformer,
    sentences: list[str],
) -> np.ndarray:
    """Wrap around sentence_transformer.encode that casts the result to numpy array.

    To compute the similarity you can use::

        from sklearn.metrics.pairwise import cosine_similarity
        sim = cosine_similarity(enc0, enc1)
    """
    encodings = cast(
        Tensor,
        sentence_transformer.encode(sentences, convert_to_tensor=True),
    )
    encodings = encodings.detach().cpu().numpy()
    return encodings


def match_similarity(
    sim: np.ndarray, chap_src: Chapter, chap_dst: Chapter, win_len: int = 20
):
    """Compute the matches between sentences in the two chapters."""
    # number of sentences in the two chapters
    sent_num_src = chap_src.sents_num
    sent_num_dst = chap_dst.sents_num
    ratio = sent_num_src / sent_num_dst

    # first iteration of matching
    all_good_max = []
    all_good_i = []

    for i in range(sent_num_src):

        # the similarity of this src sent to all the translated ones
        this_sent_sim = sim[i]

        # find the center rescaled because there are different number of sents in the two chapters
        ii = int(i / ratio)

        # the chopped similarity array
        win_left = max(0, ii - win_len)
        win_right = min(sent_num_dst, ii + win_len + 1)
        some_sent_sim = this_sent_sim[win_left:win_right]

        # the dst sent id with highest similarity
        max_id = some_sent_sim.argmax() + win_left

        # only save the results if the docs are long enough
        if (
            len(chap_src.sents_doc_orig[i]) > 4
            and len(chap_dst.sents_doc_tran[max_id]) > 4
        ):
            all_good_i.append(i)
            all_good_max.append(max_id)

    # fit a line on the matches
    fit_coeff = np.polyfit(all_good_i, all_good_max, 1)
    fit_func = np.poly1d(fit_coeff)

    # build a triangular filter to give more relevance to sentences close to the fit
    triang_height = 1
    triang_filt = triang(win_len * 4 + 1) * triang_height + (1 - triang_height)
    triang_center = win_len * 2 + 1

    all_max_rescaled = []
    all_good_i_rescaled = []
    all_good_max_rescaled = []

    for i in range(sent_num_src):

        # the similarity of this english sent to all the translated ones
        this_sent_sim = sim[i]

        # find the center rescaled because there are different number of sent in the two chapters
        ii = int(i / ratio)

        # the chopped similarity array, centered on ii
        win_left = max(0, ii - win_len)
        win_right = min(sent_num_dst, ii + win_len + 1)
        some_sent_sim = this_sent_sim[win_left:win_right]

        # the fit along the line
        ii_fit = fit_func([i])[0]
        ii_fit = int(ii_fit)
        if ii_fit < 0:
            ii_fit = 0
        if ii_fit >= sent_num_dst:
            ii_fit = sent_num_dst - 1
        # print(f"{i=} {ii=} {ii_fit=}")

        # chop the filter, centering the apex on the fitted line ii_fit
        # the apex is in win_len*2+1
        # the similarity is centered on ii
        # the shifted filter is still win_len*2+1 long
        delta_ii_fit = ii - ii_fit
        filt_edge_left = triang_center + delta_ii_fit - win_len - 1
        filt_edge_right = triang_center + delta_ii_fit + win_len + 0
        triang_filt_shifted = triang_filt[filt_edge_left:filt_edge_right]

        # chop the filter as well, if the similarity is near the border
        if ii < win_len:
            triang_filt_chop = triang_filt_shifted[win_len - ii :]
        elif ii > sent_num_dst - (win_len + 1):
            left_edge = sent_num_dst - (win_len + 1)
            triang_filt_chop = triang_filt_shifted[: -(ii - left_edge)]
        else:
            triang_filt_chop = triang_filt_shifted

        # print( f"{i=} {ii=} {ii-win_len=} {ii+win_len+1=} {len(some_sent_sim)=} {len(triang_filt_chop)=}")
        assert len(triang_filt_chop) == len(some_sent_sim)

        # rescale the similarity
        sim_rescaled = some_sent_sim * triang_filt_chop

        # find the max similarity on the rescaled sim array
        max_id_rescaled = sim_rescaled.argmax() + win_left
        all_max_rescaled.append(max_id_rescaled)

        # keep if both sents are long
        if (
            len(chap_src.sents_doc_orig[i]) > 4
            and len(chap_dst.sents_doc_tran[max_id_rescaled]) > 4
        ):
            all_good_i_rescaled.append(i)
            all_good_max_rescaled.append(max_id_rescaled)

    fig, ax = plt.subplots()
    ax.scatter(all_good_i, all_good_max, s=0.1)
    ax.plot([0, sent_num_src], [0, sent_num_dst], linewidth=0.3)
    fit_y = fit_func([0, sent_num_src])
    ax.plot([0, sent_num_src], fit_y)
    ax.plot(all_good_i_rescaled, all_good_max_rescaled, linewidth=0.9)
    ax.set_title(f"Matching")
    ax.set_ylabel("")
    ax.set_xlabel("")
    st.pyplot(fig)