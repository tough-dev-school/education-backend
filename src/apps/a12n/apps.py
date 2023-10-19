from django.apps import AppConfig


class A12NConfig(AppConfig):
    name = "apps.a12n"

    def ready(self) -> None:
        import apps.a12n.signals.handlers  # noqa
