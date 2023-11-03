from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StudyingConfig(AppConfig):
    name = "apps.studying"

    verbose_name = _("Studying")
    verbose_name_plural = _("Studying")

    def ready(self) -> None:
        """Register all shipping algorithms for the factory"""
        import apps.studying.shipment  # noqa
