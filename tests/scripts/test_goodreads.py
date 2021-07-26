import json
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from der_py.scripts import goodreads


@pytest.fixture
def mock_pool():
    _pool = MagicMock()
    _pool.return_value.__enter__.return_value.map = map
    return _pool


@pytest.fixture
def mock_ratings():
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


@pytest.mark.wip
def test_goodreads_invoke(runner: CliRunner, mock_pool, mock_ratings):
    module = "der_py.scripts.goodreads"
    csv_fixture = Path(__file__).parent / "fixture.csv"

    rating_gen = MagicMock()
    rating_gen.side_effect = iter(mock_ratings["api_ratings"])

    with patch(
        f"{module}.get_book_ratings",
        rating_gen,
    ), patch(f"{module}.Pool", mock_pool):
        result = runner.invoke(goodreads.main, csv_fixture.as_posix())
        res: List[goodreads._Record] = json.loads(result.stdout)
        assert {float(_["average_rating"]) for _ in res} == mock_ratings[
            "average_ratings"
        ]
        assert {float(_["deviant_rating"]) for _ in res} == mock_ratings[
            "deviant_ratings"
        ]
        assert result.exit_code == 0
