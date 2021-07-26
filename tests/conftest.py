import click.testing
import pytest
import requests.exceptions
from requests_mock import ANY as ANY_URL


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end test")


@pytest.fixture
def runner():
    return click.testing.CliRunner()


@pytest.fixture
def mock_wiki_get(requests_mock):
    return requests_mock.get(
        ANY_URL,
        json={
            "title": "Lorem Ipsum",
            "extract": "Lorem ipsum dolor sit amet",
        },
    )


@pytest.fixture
def mock_wiki_get_bad_json(requests_mock):
    return requests_mock.get(ANY_URL, json="random")


@pytest.fixture
def mock_wiki_error(requests_mock):
    return requests_mock.get(ANY_URL, exc=requests.RequestException)
