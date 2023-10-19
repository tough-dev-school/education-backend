from django.utils.translation import gettext_lazy as _

from core.models import models
from core.models import TimestampedModel


class Group(TimestampedModel):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _("Analytical group")
        verbose_name_plural = _("Analytical groups")
