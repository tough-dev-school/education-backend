from django.utils.translation import gettext_lazy as _

from app.models import models
from app.models import TimestampedModel


class PersonalEmailDomain(TimestampedModel):
    name = models.CharField(max_length=20, null=False, unique=True)

    class Meta:
        verbose_name = _("Personal email domain")
        verbose_name_plural = _("Personal email domains")
