from typing import Any, Never

from django.core.management.base import CommandError


class DisableTestCommandRunner:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def run_tests(self, *args: Any) -> Never:
        raise CommandError("Please use pytest")
