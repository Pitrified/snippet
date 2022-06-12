"""Utils to deal with with ebooks."""
import re
from collections import Counter
from pathlib import Path
from typing import cast

import numpy as np
import spacy
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
