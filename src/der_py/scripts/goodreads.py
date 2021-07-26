"""Do Goodreads stuff."""
import csv
import json
from dataclasses import asdict, dataclass
from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Iterable, NamedTuple, Sequence

from der_py.clients.goodreads import RatingFetcher, get_book_ratings

Record = Dict[str, str]


class _Rating(NamedTuple):
    five: int = 0
    four: int = 0
    three: int = 0
    two: int = 0
    one: int = 0

    @property
    def deviant(self) -> float:
        """Deviant rating: five stars + one stars / three stars."""
        divident = self.three
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
    def from_record(cls, record: Record) -> "_Book":
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
        fetcher: RatingFetcher = get_book_ratings,
    ) -> "_RatedBook":
        return cls(book=book, rating=_Rating(*fetcher(book.book_id)))

    def as_record(self) -> Record:
        return {
            **asdict(self.book),
            "deviant_rating": f"{self.rating.deviant:0.3f}",
            "average_rating": f"{self.rating.average:0.3f}",
            "ratings": tuple(self.rating),
        }


def _read_csv(csv_path: Path) -> Iterable[Record]:
    with open(csv_path.as_posix(), newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            yield {_normalize_key(k): v for k, v in row.items()}


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


if __name__ == "__main__":
    deviant_sorted_books = _process_csv_export(
        Path("/home/karelian/Downloads/goodreads_library_export.csv")
    )
    Path("/home/karelian/Downloads/deviant_books.json").write_text(
        json.dumps([_.as_record() for _ in deviant_sorted_books])
    )
    print("done.")
