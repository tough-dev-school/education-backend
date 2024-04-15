from typing import Callable

from django.http import HttpRequest, HttpResponse

from core.current_user import set_current_user, unset_current_user


def set_global_user(get_response: Callable[[HttpRequest], HttpResponse]) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        set_current_user(request.user)

        response = get_response(request)

        unset_current_user()

        return response

    return middleware
