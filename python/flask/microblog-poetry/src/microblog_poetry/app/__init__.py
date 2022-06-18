"""Initialize app package."""
from flask import Flask

app = Flask(__name__)

from microblog_poetry.app import routes
