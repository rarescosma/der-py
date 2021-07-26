from unittest.mock import patch

import pytest

from der_py import __main__


def test_main_succeeds(runner, mock_wiki_get):
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0


def test_main_prints_title(runner, mock_wiki_get):
    result = runner.invoke(__main__.main)
    assert "Lorem Ipsum" in result.output


def test_main_invokes_requests_get(runner, mock_wiki_get):
    _ = runner.invoke(__main__.main)
    assert mock_wiki_get.called


def test_main_uses_en_wikipedia_org(runner, mock_wiki_get):
    runner.invoke(__main__.main)
    assert mock_wiki_get.last_request.hostname == "en.wikipedia.org"


def test_main_handles_request_errors(runner, mock_wiki_error):
    result = runner.invoke(__main__.main)
    assert "Error" in result.stderr
    assert result.exit_code == 1


def test_main_uses_specified_language(runner):
    with patch("der_py.clients.wiki.random_page") as random_page:
        runner.invoke(__main__.main, ["--language=ro"])
        random_page.assert_called_with(language="ro")


@pytest.mark.e2e
def test_main_succeeds_in_production_env(runner):
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0
