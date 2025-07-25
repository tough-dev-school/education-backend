from typing import Any

from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class LegacyRecord(TimestampedModel):
    name = models.CharField(max_length=255)
    group = models.ForeignKey("products.Group", verbose_name=_("Analytical group"), on_delete=models.PROTECT)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Record")
        verbose_name_plural = _("Records")
        db_table = "courses_record"

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Deprecated model")


class LegacyBundle(TimestampedModel):
    name = models.CharField(max_length=255)
    group = models.ForeignKey("products.Group", verbose_name=_("Analytical group"), on_delete=models.PROTECT)

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Bundle")
        verbose_name_plural = _("Bundles")
        db_table = "courses_bundle"

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Deprecated model")
