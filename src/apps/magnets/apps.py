from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MagnetsConfig(AppConfig):
    name = "apps.magnets"

    verbose_name = _("Magnets")
