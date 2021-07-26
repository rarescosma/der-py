import pytest

from der_py.clients import goodreads


@pytest.mark.parametrize(
    "response, ratings",
    [
        ("", []),
        ("bla", []),
        ("renderRatingGraph(\n[1, 2]", [1, 2]),
        ("renderRatingGraph(\n[bad json, 'bad']", []),
    ],
)
def test_get_book_ratings(requests_mock, response, ratings):
    requests_mock.get(goodreads.RATINGS_API.format(book_id=1234), text=response)
    assert goodreads.get_book_ratings(1234) == ratings
    assert requests_mock.called
