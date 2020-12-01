"""Derpy attempt at a canonical representation of Python objects.

The ambition level here is to be  "good enough" for our purposes of comparing
code-generated Python files.
"""

from collections.abc import Sequence
from datetime import timedelta
from functools import partial
from typing import Any, Callable, Dict, Iterable, Type, Union

from .encoder import IntoDict

BASE_TYPES = {int, float, complex, range, bytes, str, timedelta}
ITERABLE_TYPES = {list, tuple, set, frozenset}
MAPPING_TYPES = {dict}
OBJECT_TYPES = {IntoDict}

INTERESTING_TYPES = BASE_TYPES | ITERABLE_TYPES | MAPPING_TYPES | OBJECT_TYPES

Jsonable = Union[str, list, dict, tuple]


def is_interesting(t: Type) -> bool:
    """Return True if we're dealing with an interesting type."""
    return t in INTERESTING_TYPES or hasattr(t, "__dict__")


def repr_object(o: Union[object, IntoDict]) -> Jsonable:
    """Canonical representation of an object."""
    if isinstance(o, IntoDict):
        return _repr_mapping(o.dict())
    return _repr_mapping(o.__dict__)


def _repr_mapping(m: Dict[str, Any]) -> Jsonable:
    """Represent a mapping recursively."""
    interesting = {k: v for k, v in m.items() if is_interesting(type(v))}
    hasher = partial(_repr_type, items=interesting)

    return {
        **hasher(_type_filter(MAPPING_TYPES), _repr_mapping),
        **hasher(_type_filter(BASE_TYPES), _repr_base),
        **hasher(_type_filter(ITERABLE_TYPES), _repr_iterable),
        **hasher(_type_filter(OBJECT_TYPES), repr_object),
    }


def _repr_base(
    x: Union[int, float, complex, range, bytes, str, timedelta]
) -> Jsonable:
    """Represent a base type."""
    if isinstance(x, range):
        return list(x)
    return str(x)


def _repr_iterable(xs: Union[list, tuple, set, frozenset]) -> Jsonable:
    """Represent a supported iterable."""
    return tuple(xs) if isinstance(xs, Sequence) else tuple(sorted(xs))


def _repr_type(
    _filter: Callable[[Any], bool], reprer: Callable, items: Dict[str, Any]
) -> dict:
    _keys = sorted(k for k, v in items.items() if _filter(v))
    return {k: reprer(items[k]) for k in _keys}


def _type_filter(types: Iterable[Type]) -> Callable[[Any], bool]:
    return lambda _: isinstance(_, tuple(types))
