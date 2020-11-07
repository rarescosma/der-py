from dataclasses import dataclass

import click
import requests

API_URL: str = (
    "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"
)


@dataclass(frozen=True)
class Page:
    title: str
    extract: str


def random_page(language: str = "en") -> Page:
    try:
        with requests.get(API_URL.format(language=language)) as response:
            response.raise_for_status()
            data = response.json()
            return Page(
                title=data.get("title", ""),
                extract=data.get("extract", ""),
            )
    except requests.RequestException as err:
        raise click.ClickException(str(err)) from err
