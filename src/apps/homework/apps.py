from django.apps import AppConfig


class HomeworkConfig(AppConfig):
    name = "apps.homework"

    def ready(self) -> None:
        import apps.homework.signals.handlers  # noqa
