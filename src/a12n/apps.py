from django.apps import AppConfig


class A12NConfig(AppConfig):
    name = "a12n"

    def ready(self) -> None:
        from a12n import signals  # noqa
