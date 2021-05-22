from django.apps import AppConfig


class StudyingConfig(AppConfig):
    name = 'studying'

    def ready(self):
        """Register all shipping algorithms for the factory"""
        import studying.shipment  # noqa
