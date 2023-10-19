from django.db.models import Index
from django.db.models import UniqueConstraint

from core.models import models
from core.models import TimestampedModel


class Study(TimestampedModel):
    student = models.ForeignKey("users.User", on_delete=models.CASCADE)
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE)
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE)

    homework_accepted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            Index(fields=["student", "course"]),
        ]
        constraints = [
            UniqueConstraint(fields=["student", "course"], name="unique_student_course_study"),
        ]

    def __str__(self) -> str:
        return f"{self.student} / {self.course}"
