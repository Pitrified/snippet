"""Sample app to use big modelz."""

from livereload import Server

from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename


from flask_app import app


if __name__ == "__main__":

    # remember to use DEBUG mode for templates auto reload
    # https://github.com/lepture/python-livereload/issues/144
    app.debug = True
    server = Server(app.wsgi_app)
    server.serve()
