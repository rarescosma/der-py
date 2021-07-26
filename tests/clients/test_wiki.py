import click
import pytest

from der_py.clients import wiki


def test_random_page_uses_given_language(mock_wiki_get):
    wiki.random_page(language="de")
    assert mock_wiki_get.last_request.hostname == "de.wikipedia.org"


def test_random_page_returns_page(mock_wiki_get):
    page = wiki.random_page()
    assert isinstance(page, wiki.Page)


def test_random_page_handles_validation_errors(mock_wiki_get_bad_json):
    with pytest.raises(click.ClickException):
        wiki.random_page()
