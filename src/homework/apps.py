from django.apps import AppConfig


class HomeworkConfig(AppConfig):
    name = "homework"

    def ready(self) -> None:
        import homework.signals.handlers  # noqa
