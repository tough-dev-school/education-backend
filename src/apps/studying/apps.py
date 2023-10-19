from django.apps import AppConfig


class StudyingConfig(AppConfig):
    name = "apps.studying"

    def ready(self) -> None:
        """Register all shipping algorithms for the factory"""
        import apps.studying.shipment  # noqa
