from typing import Any

from django.utils.translation import gettext_lazy as _

from apps.products.models.base import Shippable
from core.integrations.s3 import AppS3
from core.models import models


class Record(Shippable):
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE)

    s3_object_id = models.CharField(max_length=512)
    template_id = models.CharField(_("Postmark template_id"), max_length=256, blank=True, null=True, help_text=_("Leave it blank for the default template"))

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Record")
        verbose_name_plural = _("Records")
        db_table = "courses_record"

    @property
    def name_genitive(self) -> str:
        return self.course.name_genitive

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Deprecated model")

    def get_url(self, expires: int = 30 * 24 * 60 * 60) -> str:
        return AppS3().get_presigned_url(self.s3_object_id, expires=expires)

    def __str__(self) -> str:
        return f"Запись {self.name_genitive}"
