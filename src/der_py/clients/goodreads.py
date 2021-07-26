"""Goodreads client."""
import json
from typing import Callable, Sequence

import requests

Ratings = Sequence[int]
RATINGS_API: str = (
    "https://www.goodreads.com/book/delayable_book_show/{book_id}?page=1"
)

RatingFetcher = Callable[[int], Ratings]


def get_book_ratings(book_id: int) -> Ratings:
    """Fetch ratings for the given book ID."""
    print(f"fetching book ratings for book ID: {book_id}")
    lines = requests.get(RATINGS_API.format(book_id=book_id)).text.splitlines()
    idxs = [
        idx for idx, line in enumerate(lines) if "renderRatingGraph(" in line
    ]
    if not idxs:
        return []

    return [int(_) for _ in (json.loads(lines[idxs[0] + 1].strip(" ,")))]
