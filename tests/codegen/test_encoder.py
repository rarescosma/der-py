import json
from datetime import timedelta
from enum import Enum, auto

import pytest

from der_py.codegen.encoder import DUMP


class _Foo(Enum):
    bar = auto()
    baz = auto()


class _Bar:
    amazing: str = "amazing"

    def dict(self) -> dict:
        return {"it's": self.amazing}


@pytest.mark.parametrize(
    "to_encode, expected",
    [
        ({}, {}),
        (
            {
                "an_enum": _Foo.bar,
                "another_enum": _Foo.baz,
            },
            {
                "an_enum": "_Foo.bar",
                "another_enum": "_Foo.baz",
            },
        ),
        ({"dictable": _Bar()}, {"dictable": {"it's": _Bar.amazing}}),
        (
            {"deltas": timedelta(days=10, seconds=17)},
            {"deltas": "10 days, 0:00:17"},
        ),
    ],
    ids=[
        "trivial",
        "supports-enum",
        "supports-dictable-models",
        "supports-timedelta",
    ],
)
def test_dump(to_encode, expected):
    assert json.loads(DUMP(to_encode)) == expected


def test_dump_raises():
    """Should raise when encountering random objects."""
    with pytest.raises(TypeError):
        DUMP({"foo": object()})
