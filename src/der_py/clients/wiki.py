"""Client for the Wikipedia REST API."""
from dataclasses import dataclass
from functools import lru_cache
from typing import Type

import click
import requests
from desert import schema
from marshmallow import EXCLUDE, Schema, ValidationError

API_URL: str = (
    "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"
)


@dataclass(frozen=True)
class Page:
    """Wikipedia page model."""

    title: str
    extract: str


def random_page(language: str = "en") -> Page:
    """Fetch a random page from the Wikipedia API."""
    try:
        with requests.get(API_URL.format(language=language)) as response:
            response.raise_for_status()
            return _schema(of=Page).load(response.json())
    except (requests.RequestException, ValidationError) as err:
        raise click.ClickException(str(err)) from err


@lru_cache(maxsize=64)
def _schema(of: Type) -> Schema:
    return schema(of, meta={"unknown": EXCLUDE})
