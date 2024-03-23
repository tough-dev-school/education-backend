from typing import Callable

from django.http import HttpRequest, HttpResponse
from ipware import get_client_ip  # type: ignore[import-untyped]


def real_ip_middleware(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable[[HttpRequest], HttpResponse]:
    """Set REMOTE_ADDR for ip guessed by django-ipware.
    We need this to make sure all apps using remote ip are usable behind any kind of
    reverse proxy.
    If this does not work as you exepcted, check out django-ipware docs to configure it
    for your local needs: https://github.com/un33k/django-ipware
    """

    def middleware(request: HttpRequest) -> HttpResponse:
        request.META["REMOTE_ADDR"] = get_client_ip(request)[0]

        return get_response(request)

    return middleware
