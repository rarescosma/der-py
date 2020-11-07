""" Console entrypoint. """
import textwrap

import click

from der_py.clients import wiki
from . import __version__


@click.command()
@click.option(
    "--language",
    "-l",
    default="en",
    help="Language edition of Wikipedia",
    metavar="LANG",
    show_default=True,
)
@click.version_option(version=__version__)
def main(language: str) -> None:
    """A derpy python project."""
    data = wiki.random_page(language=language)
    title = data["title"]
    extract = data["extract"]

    click.secho(title, fg="green")
    click.echo(textwrap.fill(extract))
