"""Init to make this folder a package."""

from flask import Flask


print(f"Initialize Flask app with {__name__=}")

app = Flask(__name__)
app.secret_key = "any random string"

# global state
gs = {}

print("__init__.py is going to import routes")

from flask_app import routes
