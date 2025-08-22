import random
import string
import uuid
from urllib.parse import parse_qsl, urlparse, urlunparse


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


def is_valid_uuid(value: str | None) -> bool:
    """
    Validate uuid4
    You can find this method as is_uuid or is_uuid4
    """
    if value is None:
        return False

    try:
        uuid.UUID(hex=value, version=4)
    except (AttributeError, ValueError):
        return False

    return True
