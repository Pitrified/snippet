"""Sample app to show a plot.

In the plotter.html jinja2 template use the following <img> to add the plot::

    <img src="{{ image }}"/>
"""
import base64
import io

from livereload import Server
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from flask import Flask, render_template

app = Flask(__name__)

# remember to use DEBUG mode for templates auto reload
# https://github.com/lepture/python-livereload/issues/144
app.debug = True


@app.route("/", methods=["GET"])
def plotView():
    """Generate and show a plot."""
    # Generate plot
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("title")
    axis.set_xlabel("x-axis")
    axis.set_ylabel("y-axis")
    axis.grid()
    axis.plot(range(5), range(5), "ro-")

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode("utf8")

    return render_template("plotter.html", image=pngImageB64String)


if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.serve()
