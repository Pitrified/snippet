"""A translation pipeline with a basic cache.

And by basic I mean a JSON file that gets *completely* rewritten every time.
"""

import json
from pathlib import Path
from typing import Optional

from transformers.pipelines.text2text_generation import TranslationPipeline


class TranslationPipelineCache:
    """A cached translation pipeline."""

    def __init__(
        self,
        pipe: Optional[TranslationPipeline],
        cache_file_path: Path,
        lang_orig: str,
        lang_dest: str,
    ):
        """Initialize a cached TranslationPipeline."""
        self.pipe = pipe
        self.cache_file_path = cache_file_path
        self.lang_orig = lang_orig
        self.lang_dest = lang_dest

        if not cache_file_path.exists():
            self.cached_tran = {}
            return

        self.cached_tran = json.loads(cache_file_path.read_text())

    def __call__(self, str_orig: str):
        """Call an instance of the class with a string to return the translation."""
        if str_orig not in self.cached_tran:

            if self.pipe is None:
                print(f"WARNING: no loaded pipeline and unknown sentence.")
                return "UNKNOWN SENTENCE"

            str_tran = self.pipe(str_orig)
            self.cached_tran[str_orig] = str_tran[0]["translation_text"]
            self.cache_file_path.write_text(json.dumps(self.cached_tran, indent=4))

        return self.cached_tran[str_orig]
