"""Routes for the flask app."""
from flask import render_template
from microblog_poetry.app import app


@app.route("/")
@app.route("/index")
def index():
    """Render the index page."""
    user = {"username": "Miguel"}
    posts = [
        {"author": {"username": "John"}, "body": "Beautiful day in Portland!"},
        {"author": {"username": "Susan"}, "body": "The Avengers movie was so cool!"},
        {"author": {"username": "Alice"}, "body": "I will send encrypted data to Bob."},
    ]
    return render_template("index.html", title="Home", user=user, posts=posts)
