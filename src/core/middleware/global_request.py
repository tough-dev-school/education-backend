from typing import Callable

from django.http import HttpRequest, HttpResponse

from core.request import set_request, unset_request


def set_global_request(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        set_request(request)  # type: ignore

        response = get_response(request)

        unset_request()

        return response

    return middleware
