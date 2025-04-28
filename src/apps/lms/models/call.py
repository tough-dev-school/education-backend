from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from core.models import TimestampedModel, models


class Call(TimestampedModel):
    name = models.CharField(_("Name"), max_length=255)
    url = models.URLField(_("URL"), max_length=255)

    class Meta:
        verbose_name = pgettext_lazy("lms", "Call")
        verbose_name_plural = pgettext_lazy("lms", "Calls")
