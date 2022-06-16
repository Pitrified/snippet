"""Simple flask app with buttons."""
from flask import Flask, render_template, request
from livereload import Server

app = Flask(__name__)

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True


@app.route("/<int:btn>")
def button_gen(btn):
    """Generate buttons!."""
    print(f"got {btn=}")
    buttons = [0, 1, 2, 3, 4]
    info_zip = [(f"Sent {i}", f"Phrase {i}", i) for i in range(8)]
    highlight_id = 4
    return render_template(
        "buttoner.html", buttons=buttons, info_zip=info_zip, highlight_id=highlight_id
    )


@app.route("/")
def index():
    """Generate buttons!."""
    buttons = [0, 1, 2, 3, 4]
    return render_template("buttoner.html", buttons=buttons)


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    # server.watch
    server.serve()
