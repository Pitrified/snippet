"""Provide routes for the app."""
from flask import render_template, session
from transformers.pipelines import pipeline

from flask_app import app, gs
from flask_app.utils import pipe_loader


@app.route("/")
def index():
    """Render the main page of the app."""
    pipe_loader()
    tran = gs["pipeline"]("Does the pipeline work for translation tasks?")
    print(f"translation {tran}")
    return render_template("index.html")
