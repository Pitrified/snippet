"""Wrapper on the app to livereload it."""
from livereload import Server

from microblog_poetry.app import app


def main():
    """Serve the app."""
    # remember to use DEBUG mode for templates auto reload
    # https://github.com/lepture/python-livereload/issues/144
    app.debug
    server = Server(app.wsgi_app)
    server.serve()


if __name__ == "__main__":
    main()
