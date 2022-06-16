"""Simple flask app with buttons."""
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Index render."""
    if request.method == "POST":
        print(f"{request=}")
        print(f"{request.form=}")
        if request.form.get("action1") == "VALUE1":
            pass  # do something
        elif request.form.get("action2") == "VALUE2":
            pass  # do something else
        else:
            pass  # unknown

    elif request.method == "GET":
        return render_template("index.html")

    return render_template("index.html")
