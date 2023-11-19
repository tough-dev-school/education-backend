from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class PersonalEmailDomain(TimestampedModel):
    name = models.CharField(max_length=20, null=False, unique=True)

    class Meta:
        verbose_name = _("Personal email domain")
        verbose_name_plural = _("Personal email domains")
