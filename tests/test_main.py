import pytest
import requests

from der_py import __main__


@pytest.fixture
def mock_wiki_random_page(mocker):
    return mocker.patch("der_py.clients.wiki.random_page")


def test_main_succeeds(runner, mock_requests_get):
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0


def test_main_prints_title(runner, mock_requests_get):
    result = runner.invoke(__main__.main)
    assert "Lorem Ipsum" in result.output


def test_main_invokes_requests_get(runner, mock_requests_get):
    _ = runner.invoke(__main__.main)
    assert mock_requests_get.called


def test_main_uses_en_wikipedia_org(runner, mock_requests_get):
    runner.invoke(__main__.main)
    args, _ = mock_requests_get.call_args
    assert "en.wikipedia.org" in args[0]


def test_main_fails_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = Exception("Boom")
    result = runner.invoke(__main__.main)
    assert result.exit_code == 1


def test_main_prints_message_on_request_error(runner, mock_requests_get):
    mock_requests_get.side_effect = requests.RequestException
    result = runner.invoke(__main__.main)
    assert "Error" in result.output


def test_main_uses_specified_language(runner, mock_wiki_random_page):
    runner.invoke(__main__.main, ["--language=ro"])
    mock_wiki_random_page.assert_called_with(language="ro")


@pytest.mark.e2e
def test_main_succeeds_in_production_env(runner):
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0
