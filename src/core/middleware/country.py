from typing import Callable

from rest_framework.response import Response

from core.types import Request


class CountryMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        request.country_code = self.get_country_code(request)

        return self.get_response(request)

    @staticmethod
    def get_country_code(request: Request) -> str:
        if "cf-ipcountry" in request.headers:
            return request.headers["cf-ipcountry"]

        return "XX"
