from django.db.models import Index, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Study(TimestampedModel):
    student = models.ForeignKey("users.User", on_delete=models.CASCADE, verbose_name=_("Student"))
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE, verbose_name=_("Course"))
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, verbose_name=_("Order"))

    homework_accepted = models.BooleanField(default=False, verbose_name=_("Homework accepted"))

    class Meta:
        indexes = [
            Index(fields=["student", "course"]),
        ]
        constraints = [
            UniqueConstraint(fields=["student", "course"], name="unique_student_course_study"),
        ]
        verbose_name = _("Study")
        verbose_name_plural = _("Studies")

    def __str__(self) -> str:
        return f"{self.student} / {self.course}"
