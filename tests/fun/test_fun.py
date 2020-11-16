from operator import itemgetter

import pytest

from der_py.fun import (
    compose,
    extract,
    flatmap,
    jaccard,
    key_by,
    mask_dict,
    pairwise,
    scrub,
    slice_dict,
    split_by,
)


@pytest.mark.parametrize(
    "f, xs, res",
    [
        (lambda a: [a, a + 1], [1, 2, 3], [1, 2, 2, 3, 3, 4]),
        (lambda a: [a], [1, 2, 3], [1, 2, 3]),
        (lambda a: [a], [], []),
        (lambda a: [], [1, 2], []),
    ],
)
def test_flatmap(f, xs, res):
    assert list(flatmap(f, xs)) == res


@pytest.mark.parametrize(
    "d, res",
    [
        ({}, {}),
        ({"a": None}, {}),
        ({"a": None, "b": None}, {}),
        ({"a": None, "b": 2}, {"b": 2}),
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
    ],
)
def test_scrub(d, res):
    assert scrub(d) == res


@pytest.mark.parametrize(
    "d, keys, res",
    [
        ({}, "", {}),
        ({}, "a", {}),
        ({"a": 1}, "X", {}),
        ({"a": 1}, "a", {"a": 1}),
        ({"a": None}, "a", {"a": None}),
        ({"a": 1, "b": 2}, "a", {"a": 1}),
        ({"a": 1, "b": 2}, "aX", {"a": 1}),
        ({"a": 1, "b": 2, "c": 3}, "ac", {"a": 1, "c": 3}),
    ],
)
def test_slice_dict(d, keys, res):
    assert slice_dict(d, set(keys)) == res


@pytest.mark.parametrize(
    "d, keys, res",
    [
        ({}, "", {}),
        ({}, "a", {}),
        ({"a": 1}, "X", {"a": 1}),
        ({"a": 1}, "a", {}),
        ({"a": None}, "a", {}),
        ({"a": 1, "b": 2}, "b", {"a": 1}),
        ({"a": 1, "b": 2}, "bX", {"a": 1}),
        ({"a": 1, "b": 2, "c": 3}, "ac", {"b": 2}),
    ],
)
def test_mask_dict(d, keys, res):
    assert mask_dict(d, set(keys)) == res


@pytest.mark.parametrize(
    "seq, key, res",
    [
        ((), lambda x: 1 / 0, {}),
        (
            "aabbb",
            lambda x: x,
            {
                "a": ["a", "a"],
                "b": ["b", "b", "b"],
            },
        ),
        ("abc", str.islower, {True: ["a", "b", "c"]}),
        (
            "aBcD",
            str.islower,
            {
                True: ["a", "c"],
                False: ["B", "D"],
            },
        ),
        (
            "aBAb",
            str.lower,
            {
                "a": ["a", "A"],
                "b": ["B", "b"],
            },
        ),
    ],
)
def test_key_by(seq, key, res):
    assert key_by(key, seq) == res


@pytest.mark.parametrize(
    "fun, seq, res",
    [
        (lambda x: x, [True, False, 1], ([False], [True, 1])),
    ],
)
def test_split_by(fun, seq, res):
    assert split_by(fun, seq) == res


@pytest.mark.parametrize(
    "x, extractors, expected",
    [
        ({}, [], None),
        ({}, [itemgetter("a")], None),
        ({"a": "b"}, [itemgetter("a")], "b"),
        ({"a": "b"}, [itemgetter("z"), itemgetter("a")], "b"),
        ({"a": "b"}, [lambda _: False, itemgetter("a")], "b"),
    ],
    ids=[
        "trivial",
        "no-exc",
        "it-exists",
        "second-is-the-lucky-one",
        "falsy-first",
    ],
)
def test_extract(x, extractors, expected):
    assert expected == extract(x, extractors)


@pytest.mark.parametrize(
    "a, b, res",
    [
        ("", "", 0.0),
        ("a", "b", 0.0),
        ("a", "a", 1.0),
        ("abc", "bcd", 0.5),
    ],
)
def test_jaccard(a, b, res):
    assert jaccard(a, b) == res


@pytest.mark.parametrize(
    "xs, res",
    [
        ([], []),
        ("a", []),
        ("ab", [("a", "b")]),
        ("abcde", [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e")]),
    ],
)
def test_pairwise(xs, res):
    assert list(pairwise(xs)) == res


@pytest.mark.parametrize(
    "fns, arg, res",
    [
        ((), "foo", "foo"),
        ((str.lower, str.upper), "aAa", "AAA"),
        ((str.lower, str.upper, str.lower), "aAa", "aaa"),
        ((lambda _: _ * 2, sum), [1, 2, 3], 12),
    ],
)
def test_compose(fns, arg, res):
    assert compose(*fns)(arg) == res
