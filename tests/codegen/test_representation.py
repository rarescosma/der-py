from collections import OrderedDict
from types import SimpleNamespace

import pytest

from der_py.codegen.representation import repr_object


class Dictable:
    amazing: str = "amazing"

    def dict(self) -> dict:
        return {"it's": self.amazing}


@pytest.mark.parametrize(
    "in_obj, expected",
    [
        (SimpleNamespace(), {}),
        (
            SimpleNamespace(
                ints=42,
                floats=3.14,
                complex=complex(1, -1),
                ranges=range(3),
                bytes=b"foo",
                strings="vitlök",
            ),
            {
                "ints": "42",
                "floats": "3.14",
                "complex": "(1-1j)",
                "ranges": [0, 1, 2],
                "bytes": "b'foo'",
                "strings": "vitlök",
            },
        ),
        (
            SimpleNamespace(
                a_list=[1, 2, 3],
                a_tuple=(3, 2, 1),
                a_homogenous_set={"heh", "foo"},
                an_icy_set=frozenset(["bar", "akku"]),
            ),
            {
                "a_homogenous_set": ("foo", "heh"),
                "a_list": (1, 2, 3),
                "a_tuple": (3, 2, 1),
                "an_icy_set": ("akku", "bar"),
            },
        ),
        (
            SimpleNamespace(
                a_mapping=OrderedDict({"foo": "bar", "akuuu": "lol"})
            ),
            {"a_mapping": {"foo": "bar", "akuuu": "lol"}},
        ),
        (
            SimpleNamespace(a_dictable=Dictable()),
            {"a_dictable": {"it's": "amazing"}},
        ),
    ],
    ids=["trivial", "base-types", "iterables", "mappings", "dictables"],
)
def test_can_represent_base_types(in_obj, expected):
    assert repr_object(in_obj) == expected
