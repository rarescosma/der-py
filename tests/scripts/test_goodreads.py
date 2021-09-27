import json
from pathlib import Path
from typing import List, Set, TypedDict
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from der_py.scripts import goodreads


class MockRatings(TypedDict):
    api_ratings: List[List[int]]
    average_ratings: Set[float]
    deviant_ratings: Set[float]


@pytest.fixture
def mock_ratings() -> MockRatings:
    return {
        # order: 5, 4, 3, 2, 1
        "api_ratings": [
            [1, 1, 1, 1, 1],
            [7, 3, 0, 2, 4],
            [4, 0, 0, 0, 1],
            [0, 0, 0, 0, 0],
        ],
        "average_ratings": {3.0, 3.4375, 4.2, 0.0},
        "deviant_ratings": {2.0, 4.4, 0.0},
    }


@pytest.fixture()
def mock_csv_export():
    csv_file = Path(__file__).parent / "fixture.csv"
    return csv_file.as_posix()


def test_goodreads_invoke(
    runner: CliRunner,
    mock_csv_export,
    mock_pool,
    mock_ratings: MockRatings,
):
    module = "der_py.scripts.goodreads"

    mock_get_book_ratings = MagicMock()
    mock_get_book_ratings.side_effect = iter(mock_ratings["api_ratings"])

    with (
        patch(f"{module}.Pool", mock_pool),
        patch(f"{module}.get_book_ratings", mock_get_book_ratings),
    ):
        result = runner.invoke(goodreads.main, mock_csv_export)
        res: List[goodreads._Record] = json.loads(result.stdout)

        average_ratings = {float(_["average_rating"]) for _ in res}
        assert average_ratings == mock_ratings["average_ratings"]

        deviant_ratings = {float(_["deviant_rating"]) for _ in res}
        assert deviant_ratings == mock_ratings["deviant_ratings"]

        assert result.exit_code == 0
