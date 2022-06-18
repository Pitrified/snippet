# Build a fancy app

Following
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

## Setup

```bash
poetry install
poetry run serve
```

#### Env var

```bash
export FLASK_APP=src/microblog_poetry/app/__init__.py
```

Automatically done in `.flaskenv`.

#### Serve via livereload

Directly:

```bash
python src/microblog_poetry/app/livereload_app.py
```

With magic poetry command registered in `pyproject.toml`:

```bash
poetry run serve
```