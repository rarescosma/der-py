"""Derpy JSON encoder."""
import datetime
import json
from enum import Enum
from functools import partial
from json import JSONEncoder
from typing import Any, Protocol, Union, runtime_checkable


@runtime_checkable
class IntoDict(Protocol):
    """Protocol used for duck-typing "dictable" classes.

    Used to identify models that are convertible into
    dictionaries by calling on their 'dict()' method.
    """

    def dict(self) -> dict:
        """Conversion method."""


class Encoder(JSONEncoder):
    """Encode operations for common types.

    Extend this class to provide your own representation for certain field
    types not normally handled by JSON.
    """

    # pylint: disable=method-hidden
    def default(self, obj: Any) -> Union[dict, str]:
        """Extend default encoder support with various field types."""
        if isinstance(obj, IntoDict):
            return obj.dict()
        if isinstance(obj, Enum):
            return str(obj)
        if isinstance(obj, datetime.timedelta):
            return str(obj)
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)


DUMP = partial(json.dumps, indent=2, sort_keys=True, cls=Encoder)
