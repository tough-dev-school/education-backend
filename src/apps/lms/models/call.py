from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from core.models import TimestampedModel, models
from core.video import VideoModelMixin


class Call(TimestampedModel, VideoModelMixin):
    name = models.CharField(_("Name"), max_length=255)
    url = models.URLField(_("URL"), max_length=255)

    youtube_id = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    rutube_id = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    rutube_access_key = models.CharField(max_length=256, blank=True, null=True)
    datetime = models.DateTimeField(verbose_name=pgettext_lazy("lms", "Call date"))

    class Meta:
        verbose_name = pgettext_lazy("lms", "Call")
        verbose_name_plural = pgettext_lazy("lms", "Calls")
