from django.apps import AppConfig


class HomeworkConfig(AppConfig):
    name = 'homework'

    def ready(self):
        import homework.signals.handlers  # noqa
