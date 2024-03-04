from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class MaterialFile(TimestampedModel):
    file = models.FileField(upload_to="materials", unique=True)  # NOQA: VNE002

    class Meta:
        verbose_name = _("Material file")
        verbose_name_plural = _("Material files")

    def __str__(self) -> str:
        return self.file.name

    def get_absolute_url(self) -> str:
        return self.file.url
