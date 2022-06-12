"""Load cached spacy models from a single location."""

from pathlib import Path
from timeit import default_timer

import spacy


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


def run_cache_models() -> None:
    """Use the cached model load function."""
    cache_dir = Path("~/.cache/spacy_my_models").expanduser()

    # model_path = "en_core_web_sm"
    # model_path = "en_core_web_md"
    # model_path = "en_core_web_lg"
    model_path = "fr_core_news_sm"
    # model_path = "fr_core_news_md"
    # model_path = "fr_core_news_lg"
    # model_path = "it_core_news_lg"

    start = default_timer()
    spacy_load_cached(model_path, cache_dir)
    end = default_timer()
    print(f"Loaded {model_path} from {cache_dir} in {end-start:.2f}s")


if __name__ == "__main__":
    run_cache_models()
