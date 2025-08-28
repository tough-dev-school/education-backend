from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Group(TimestampedModel):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True)

    dashamail_list_id = models.IntegerField(null=True)

    evergreen = models.BooleanField(_("Evergreen"), default=False)

    class Meta:
        verbose_name = _("Product group")
        verbose_name_plural = _("Product groups")
