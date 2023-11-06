from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiplomasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.diplomas"

    verbose_name = _("Diplomas")
    verbose_name_plural = _("Diplomas")
