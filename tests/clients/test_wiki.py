from der_py.clients import wiki


def test_random_page_uses_given_language(mock_requests_get):
    wiki.random_page(language="de")
    args, _ = mock_requests_get.call_args
    assert "de.wikipedia.org" in args[0]


def test_random_page_returns_page(mock_requests_get):
    page = wiki.random_page()
    assert isinstance(page, wiki.Page)
