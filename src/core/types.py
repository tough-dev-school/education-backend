from typing import Literal

from rest_framework.request import Request as DRFRequest

Language = Literal["ru", "en", "RU", "EN"]


class Request(DRFRequest):
    country_code: str


__all__ = [
    "Language",
    "Request",
]
