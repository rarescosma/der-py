"""Sphinx configuration."""
from datetime import date

project = "der-py"
author = "Rareș Cosma"
copyright = f"{date.today().year}, {author}"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]
