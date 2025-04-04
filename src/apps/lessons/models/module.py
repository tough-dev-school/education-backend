from django.db.models import Index
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Module(TimestampedModel):
    name = models.CharField(max_length=255)
    course = models.ForeignKey("lessons.LessonCourse", on_delete=models.CASCADE, related_name="modules")
    hidden = models.BooleanField(_("Hidden"), help_text=_("Users can't find such materials in the listing"), default=True)
    position = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            Index(fields=["course", "position"]),
        ]
