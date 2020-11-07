import click
import pytest

from der_py.clients import wiki


def test_random_page_uses_given_language(mock_requests_get):
    wiki.random_page(language="de")
    args, _ = mock_requests_get.call_args
    assert "de.wikipedia.org" in args[0]


def test_random_page_returns_page(mock_requests_get):
    page = wiki.random_page()
    assert isinstance(page, wiki.Page)


def test_random_page_handles_validation_errors(mock_requests_get):
    mock_requests_get.return_value.__enter__.return_value.json.return_value = (
        None
    )
    with pytest.raises(click.ClickException):
        wiki.random_page()
