"""Routes for the flask app."""
from microblog_poetry.app import app


@app.route("/")
@app.route("/index")
def index():
    """Render the index page."""
    return "Hello, World!"
