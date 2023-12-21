from django.utils.translation import gettext_lazy as _

from core.files import RandomFileName
from core.models import models
from core.models import TimestampedModel


class NotionAsset(TimestampedModel):
    url = models.URLField(max_length=1024, unique=True, db_index=True)
    file = models.FileField(upload_to=RandomFileName("assets"), unique=True)  # NOQA: VNE002
    size = models.IntegerField(_("Image size in bytes"))
    md5_sum = models.CharField(max_length=32)

    class Meta:
        verbose_name = _("Notion asset")
        verbose_name_plural = _("Notion assets")

    def __str__(self) -> str:
        return self.file.name

    def get_absolute_url(self) -> str:
        return self.file.url
