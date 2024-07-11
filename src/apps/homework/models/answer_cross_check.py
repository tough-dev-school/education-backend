from typing import TYPE_CHECKING

from django.db.models import Count, Index, Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models

if TYPE_CHECKING:
    from apps.homework.models import Question


class AnswerCrossCheckQuerySet(models.QuerySet):
    def visible_answers_count_for_question(self, question: "Question", answers_count: int) -> int:
        data = self.filter(answer__question=question).aggregate(checked=Count("pk", filter=Q(checked_at__isnull=False)), total=Count("pk"))
        return answers_count if data["checked"] >= data["total"] else data["checked"]


class AnswerCrossCheck(TimestampedModel):
    objects = AnswerCrossCheckQuerySet.as_manager()

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
