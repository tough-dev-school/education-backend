from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Video(TimestampedModel):
    """Video mapping for multiple videohostings"""

    youtube_id = models.CharField(max_length=32, unique=True, db_index=True)
    rutube_id = models.CharField(max_length=32, blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = _("Notion video")
        verbose_name_plural = _("Notion videos")

    def __str__(self) -> str:
        return self.youtube_id

    def get_youtube_embed_src(self) -> str:
        return f"https://www.youtube.com/embed/{ self.youtube_id }?rel=0"

    def get_rutube_embed_src(self) -> str:
        return f"https://rutube.ru/play/embed/{self.rutube_id }/"
