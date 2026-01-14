from typing import Callable

from geoip2fast import GeoIP2Fast
from rest_framework.response import Response

from core.types import Request


class CountryMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response
        self.GEOIP = GeoIP2Fast()

    def __call__(self, request: Request) -> Response:
        request.country_code = self.get_country_code(request)

        return self.get_response(request)

    def get_country_code(self, request: Request) -> str:
        result = self.GEOIP.lookup(request.META["REMOTE_ADDR"])
        if result is not None:
            return result.country_code.upper()

        return "XX"
