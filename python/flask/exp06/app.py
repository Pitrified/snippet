"""Sample app to load files."""
import base64
import io

from livereload import Server
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from flask import Flask, render_template, request

app = Flask(__name__)

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True


@app.route("/", methods=["GET", "POST"])
def file_drop():
    """Load a file."""
    filename = "Load a file!"
    if request.method == "POST":
        print(f"{request=}")
        print(f"{request.form=}")
        print(f"{request.files=}")

        uploaded_file = request.files["my-epub-file"]
        filename = uploaded_file.filename
        if uploaded_file.filename != "":
            print(f"got file {uploaded_file.filename=}")
            print(f"got file {uploaded_file.headers=}")

    return render_template("filedropper.html", filename=filename)


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve()
