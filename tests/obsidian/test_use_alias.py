from unittest.mock import MagicMock

import pytest

from der_py.obsidian.use_alias import _all_aliases


@pytest.mark.parametrize(
    "frontmatter, expected",
    [
        ({}, []),
        (
            {
                "alias": "foo",
            },
            ["foo"],
        ),
        (
            {"aliases": "foo", "alias": ["bar", "baz"]},
            ["bar", "baz", "foo"],
        ),
        (
            {"aliases": ["foo", "aaargh"], "alias": ["bar", "baz"]},
            ["aaargh", "bar", "baz", "foo"],
        ),
        (
            {"aliases": ["foo", "aaargh"], "alias": -42},
            ["aaargh", "foo"],
        ),
    ],
)
def test_all_aliases(frontmatter, expected):
    note = MagicMock()
    note.frontmatter = frontmatter

    assert _all_aliases(note) == expected
