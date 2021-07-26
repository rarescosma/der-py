"""Do Goodreads stuff."""
import csv
import json
from dataclasses import asdict, dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Iterable, NamedTuple, Sequence, Tuple, TypedDict, cast

import click

from der_py.clients.goodreads import get_book_ratings


class _Record(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    bookshelves: str
    deviant_rating: float
    average_rating: float
    rating: Tuple[int, ...]


class _Rating(NamedTuple):
    five: int = 0
    four: int = 0
    three: int = 0
    two: int = 0
    one: int = 0

    @property
    def deviant(self) -> float:
        """Deviant rating: five stars + one stars / three stars."""
        divident: float = self.three
        if self.three == 0:
            if self.four == 0 and self.two == 0:
                return 0
            # interpolate number of 3 stars from 4 and 2
            divident = (self.four + self.two) / 2
        return (self.five + self.one) / divident

    @property
    def average(self) -> float:
        """Average rating."""
        total_ratings = sum(self)
        if not total_ratings:
            return 0

        total = sum([x * r for x, r in zip(self, range(len(self), 0, -1))])
        return total / total_ratings


@dataclass(frozen=True)
class _Book:
    book_id: int
    title: str
    author: str

    @classmethod
    def from_record(cls, record: _Record) -> "_Book":
        return cls(
            book_id=record.get("book_id", -1),
            title=record.get("title", ""),
            author=record.get("author", ""),
        )


class _RatedBook(NamedTuple):
    book: _Book
    rating: _Rating

    @classmethod
    def from_book(
        cls,
        book: _Book,
    ) -> "_RatedBook":
        return cls(book=book, rating=_Rating(*get_book_ratings(book.book_id)))

    def as_record(self) -> _Record:
        return cast(
            _Record,
            {
                **asdict(self.book),
                "deviant_rating": f"{self.rating.deviant:0.4f}",
                "average_rating": f"{self.rating.average:0.4f}",
                "ratings": tuple(self.rating),
            },
        )


def _read_csv(csv_path: Path) -> Iterable[_Record]:
    with open(csv_path.as_posix(), newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            yield cast(_Record, {_normalize_key(k): v for k, v in row.items()})


def _normalize_key(key: str) -> str:
    return key.lower().replace(" ", "_")


def _process_csv_export(csv_path: Path) -> Sequence[_RatedBook]:
    books = [
        _Book.from_record(_)
        for _ in _read_csv(csv_path)
        if "to-read" in _.get("bookshelves", "")
    ]

    with Pool() as pool:
        rated_books = pool.map(_RatedBook.from_book, books)

    return sorted(rated_books, key=lambda _: _.rating.deviant, reverse=True)


@click.command()
@click.argument(
    "csv_path",
    type=click.Path(exists=True, dir_okay=False, file_okay=True),
)
def main(csv_path: str) -> None:
    """Process CSV exports from Goodreads into JSON records."""
    real_csv_path = Path(csv_path)

    deviant_sorted_books = _process_csv_export(real_csv_path)
    print(json.dumps([_.as_record() for _ in deviant_sorted_books]))
