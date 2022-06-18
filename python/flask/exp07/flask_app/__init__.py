"""Init to make this folder a package."""

from flask import Flask

app = Flask(__name__)

# global state
gs = {}

from flask_app import routes
