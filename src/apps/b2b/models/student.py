from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Student(TimestampedModel):
    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
    deal = models.ForeignKey("b2b.Deal", related_name="students", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self) -> str:
        return str(self.user)
