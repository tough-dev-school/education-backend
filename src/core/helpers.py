import random
import string
from urllib.parse import parse_qsl
from urllib.parse import urlparse
from urllib.parse import urlunparse


def lower_first(string: str) -> str:
    return string[0].lower() + string[1:]


def random_string(string_length: int) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=string_length))


def append_to_query_string(url: str, **kwargs: str) -> str:
    """Append a parameter to the url querystring"""
    parsed = list(urlparse(url))
    query = dict(parse_qsl(parsed[4]))
    query.update(kwargs)
    parsed[4] = "&".join(f"{p}={v}" for p, v in query.items())

    return urlunparse(parsed)
