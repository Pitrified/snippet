"""Sample app to load files.

https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask
"""
import base64
import io

from livereload import Server

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True


# 20Mb for an EPub
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 20


@app.route("/viaform", methods=["GET", "POST"])
def file_form():
    """Load a file."""
    filename = "Load a file"
    if request.method == "POST":
        print(f"{request=}")
        print(f"{request.form=}")
        print(f"{request.files=}")

        uploaded_file = request.files["my-epub-file"]
        if uploaded_file.filename is not None:
            filename = secure_filename(uploaded_file.filename)
        else:
            filename = "None"
        if filename != "" and filename != "None":
            print(f"got file {filename=}")
            print(f"got file {uploaded_file.headers=}")

        # return redirect(url_for("file_form"))

    return render_template("fileformer.html", filename=filename)


@app.route("/viadrop", methods=["GET", "POST"])
def file_drop():
    """Load a file with fancy drops."""
    filename = "Load something please."
    if request.method == "POST":
        print(f"{request=}")
        print(f"{request.form=}")
        print(f"{request.files=}")

        file_key = "my-awesome-dropzone-name"
        if file_key in request.files:
            uploaded_file = request.files[file_key]
            if uploaded_file.filename is not None:
                filename = secure_filename(uploaded_file.filename)
            else:
                filename = "None"
            if filename != "" and filename != "None":
                print(f"got file {filename=}")
                print(f"got file {uploaded_file.headers=}")
        else:
            filename = "Not a valid key"

    return render_template("filedropper.html", filename=filename)


@app.route("/")
def index():
    """Render the main page of the app."""
    return render_template("index.html")


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve()
