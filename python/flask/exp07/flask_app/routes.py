"""Provide routes for the app."""
from flask import render_template, session
from transformers.pipelines import pipeline

from flask_app import app, gs


def pipe_loader(lt="en", lt_other="fr"):
    """Load a pipeline and store it in the session object."""
    print(f"loading {lt} {lt_other}")
    if "pipeline" not in gs:
        print(f"loading to session")
        gs["pipeline"] = pipeline(
            "translation", model=f"Helsinki-NLP/opus-mt-{lt}-{lt_other}"
        )


@app.route("/")
def index():
    """Render the main page of the app."""
    pipe_loader()
    tran = gs["pipeline"]("Does the pipeline work for translation tasks?")
    print(f"translation {tran}")
    return render_template("index.html")
