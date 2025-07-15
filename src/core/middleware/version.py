from pathlib import Path
from typing import Callable

from django.conf import settings
from rest_framework.response import Response

from core.conf.environ import env
from core.types import Request


class VersionHeaderMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        response = self.get_response(request)

        if "localhost" not in request.get_host():
            return response

        release = env("RELEASE", default="please-set-in-the-env-var")
        running_in_container = Path.exists(Path("/.dockerenv"))
        response["X-Backend-Version"] = f"{release} (debug={settings.DEBUG}; container={running_in_container})"

        return response
