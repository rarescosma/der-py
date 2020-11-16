"""Derpy fun: higher-order functions and other shenanigans."""
from collections import defaultdict
from contextlib import suppress
from functools import reduce
from itertools import tee
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    Hashable,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
)

A = TypeVar("A")
B = TypeVar("B")
K = TypeVar("K")
V = TypeVar("V", bound=Hashable)


def flatmap(f: Callable[[A], Iterable[B]], xs: Iterable[A]) -> Iterable[B]:
    """Map f over an iterable and flatten the result set."""
    return (y for x in xs for y in f(x))


def scrub(d: Dict[K, V]) -> Dict[K, V]:
    """Remove key pair if value is None."""
    return {k: v for k, v in d.items() if v is not None}


def slice_dict(d: Dict[K, V], keys: Set[K]) -> Dict[K, V]:
    """Slice given keys out of the dictionary."""
    return {k: d[k] for k in keys if k in d}


def mask_dict(d: Dict[K, V], drop: Set[K]) -> Dict[K, V]:
    """Drop given keys from the dictionary. Opposite of slice_dict."""
    return {k: v for k, v in d.items() if k not in drop}


def key_by(f: Callable[[A], K], xs: Iterable[A]) -> DefaultDict[K, List[A]]:
    """Group seq after key."""
    d: DefaultDict[K, List[A]] = defaultdict(list)
    for it in xs:
        d[f(it)].append(it)
    return d


def split_by(
    f: Callable[[A], bool],
    xs: Iterable[A],
) -> Tuple[List[A], List[A]]:
    """Chops the iterable into two: right fulfills predicate, left doesn't."""
    _keyed = key_by(f, xs)
    return _keyed[False], _keyed[True]


def extract(
    a: K,
    extractors: Iterable[Callable[[K], Any]],
    value_type: Optional[Type[V]] = None,
) -> Optional[V]:
    """Try to extract value using a chain of extractors. None if all fails."""
    _value_type = value_type or str
    for extractor in extractors:
        with suppress(KeyError, ValueError, AttributeError):
            candidate = extractor(a)
            if isinstance(candidate, _value_type):
                return candidate
    return None


def jaccard(left: Iterable[K], right: Iterable[K]) -> float:
    """Jaccard score, also known as Jaccard index for two iterables."""
    left = set(left) if not isinstance(left, (set, frozenset)) else left
    right = set(right) if not isinstance(right, (set, frozenset)) else right
    common = len(left & right)
    unique = len(left | right)
    return 1.0 * common / unique if unique else 0.0


def pairwise(iterable: Iterable[A]) -> Iterable[Tuple[A, A]]:
    """Generate pairs of consecutive elements from the given iterable.

    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    orig, copy = tee(iterable)
    next(copy, None)
    return zip(orig, copy)


def compose(*functions: Callable) -> Callable:
    """Compose a variable # of functions."""
    return reduce(lambda f, g: lambda x: f(g(x)), functions[::-1], lambda x: x)
