# uwsgiconf installation

[uv](https://docs.astral.sh/uv/) is recommended for installation, though plain `pip` works too.

## From PyPI

Add the package to a project:

```bash
uv add uwsgiconf
```

or with pip:

```bash
pip install uwsgiconf
```

## From source

Clone the repository and synchronize its development environment:

```bash
git clone https://github.com/idlesign/uwsgiconf uwsgiconf
cd uwsgiconf
uv sync
```

Run commands in the project environment with `uv run`.
