from django.db.models import Index
from django.utils.translation import gettext_lazy as _

from apps.products.models import Course as _Course
from core.models import TimestampedModel, models


class Course(_Course):
    class Meta:
        proxy = True
        ordering = ["-created"]


class Lesson(TimestampedModel):
    name = models.CharField(max_length=255)
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE, related_name="lessons")
    position = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)
    material = models.ForeignKey("notion.Material", blank=True, null=True, related_name="+", on_delete=models.PROTECT)
    hidden = models.BooleanField(_("Hidden"), help_text=_("Users can't find such materials in the listing"), default=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            Index(fields=["course", "position"]),
        ]
