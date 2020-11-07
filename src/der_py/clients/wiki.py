import os

import click
import requests

API_URL = "https://{language}.wikipedia.org/api/rest_v1/page/random/summary"


def random_page(language: str = "en") -> dict:
    try:
        with requests.get(API_URL.format(language=language)) as response:
            response.raise_for_status()
            return response.json()
    except requests.RequestException as err:
        print(os.getcwd())
        raise click.ClickException(str(err)) from err
