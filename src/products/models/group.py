from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models


class Group(TimestampedModel):
    name = models.CharField(max_length=256)

    class Meta:
        verbose_name = _('Analytical group')
        verbose_name_plural = _('Analytical groups')
