import contextlib
from typing import Callable

from rest_framework.response import Response

from core.types import Request


class CountryMiddleware:
    def __init__(self, get_response: Callable) -> None:
        with contextlib.suppress(SyntaxError):
            from geoip2fast import GeoIP2Fast

            self.GEOIP = GeoIP2Fast()

        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        request.country_code = self.get_country_code(request)

        return self.get_response(request)

    def get_country_code(self, request: Request) -> str:
        result = self.GEOIP.lookup(request.META["REMOTE_ADDR"])
        if result is not None:
            return result.country_code.upper()

        return "XX"
