from django.utils.translation import gettext_lazy as _

from app.models import models
from app.models import TimestampedModel


class Group(TimestampedModel):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = _("Analytical group")
        verbose_name_plural = _("Analytical groups")
