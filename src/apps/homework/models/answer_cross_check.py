from django.db.models import Index, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class AnswerCrossCheck(TimestampedModel):
    answer = models.ForeignKey("homework.Answer", on_delete=models.CASCADE)
    checker = models.ForeignKey("users.User", on_delete=models.CASCADE)
    checked_at = models.DateTimeField(
        _("Date when crosscheck got checked"),
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            Index(fields=["answer", "checker"]),
        ]

        constraints = [
            UniqueConstraint(fields=["answer", "checker"], name="unique_checker_and_answer"),
        ]
