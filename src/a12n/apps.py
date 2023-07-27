from django.apps import AppConfig


class A12NConfig(AppConfig):
    name = "a12n"

    def ready(self) -> None:
        import a12n.signals.handlers  # noqa
