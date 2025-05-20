from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models
from core.video import VideoModelMixin


class Video(TimestampedModel, VideoModelMixin):
    """Video mapping for multiple videohostings"""

    title = models.CharField(_("Title"), max_length=256, blank=True, null=True)
    youtube_id = models.CharField(max_length=256, unique=True, db_index=True)
    rutube_id = models.CharField(max_length=256, blank=True, null=True, db_index=True)
    rutube_access_key = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        verbose_name = _("Notion video")
        verbose_name_plural = _("Notion videos")

    def __str__(self) -> str:
        return self.youtube_id
