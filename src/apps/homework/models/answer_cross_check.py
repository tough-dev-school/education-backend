from typing import TYPE_CHECKING

from django.db.models import Count, Index, Q, UniqueConstraint
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models

if TYPE_CHECKING:
    from apps.homework.models import Question
    from apps.users.models import User


class AnswerCrossCheckQuerySet(models.QuerySet):
    def for_viewset(self) -> "AnswerCrossCheckQuerySet":
        return self.select_related("checker", "answer", "answer__question")

    def for_user(self, user: "User") -> "AnswerCrossCheckQuerySet":
        return (
            self.filter(
                checker=user,
            )
            .exclude(
                answer__author=user,
            )
            .exclude(
                author=user,
            )
        )

    def count_for_question(self, question: "Question") -> dict[str, int]:
        return self.filter(answer__question=question).aggregate(
            checked=Count("pk", filter=Q(checked__isnull=False)),
            total=Count("pk"),
        )


class AnswerCrossCheck(TimestampedModel):
    objects = AnswerCrossCheckQuerySet.as_manager()

    author = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name="+")
    answer = models.ForeignKey("homework.Answer", on_delete=models.CASCADE)
    checker = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="+")
    checked = models.DateTimeField(
        _("Date when crosscheck got checked"),
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        indexes = [
            Index(fields=["answer", "checker"]),
            Index(fields=["answer", "checker", "checked"]),
        ]

        constraints = [
            UniqueConstraint(fields=["answer", "checker"], name="unique_checker_and_answer"),
        ]

        ordering = ["id"]
