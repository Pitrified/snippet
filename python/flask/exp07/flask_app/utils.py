"""Support functions for the app."""

from transformers.pipelines import pipeline
from flask_app import gs


def pipe_loader(lt="en", lt_other="fr"):
    """Load a pipeline and store it in the session object."""
    print(f"Loading {lt} {lt_other}")
    if "pipeline" not in gs:
        print(f"Loading to global state")
        gs["pipeline"] = pipeline(
            "translation", model=f"Helsinki-NLP/opus-mt-{lt}-{lt_other}"
        )
