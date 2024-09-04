from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Video(TimestampedModel):
    """Video mapping for multiple videohostings"""

    youtube_id = models.CharField(max_length=256, unique=True, db_index=True, help_text=_("Paste it from the address bar"))
    rutube_id = models.CharField(max_length=256, blank=True, null=True, db_index=True, help_text=_("Paste it from the address bar"))

    class Meta:
        verbose_name = _("Notion video")
        verbose_name_plural = _("Notion videos")

    def __str__(self) -> str:
        return self.youtube_id

    def get_youtube_embed_src(self) -> str:
        return f"https://www.youtube.com/embed/{ self.youtube_id }?rel=0"

    def get_youtube_url(self) -> str:
        return f"https://youtu.be/{ self.youtube_id }"

    def get_rutube_embed_src(self) -> str:
        return f"https://rutube.ru/play/embed/{self.rutube_id }/"

    def get_rutube_url(self) -> str:
        return f"https://rutube.ru/video/{ self.rutube_id }/"
