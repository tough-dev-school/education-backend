from django.db.models import Index, UniqueConstraint

from core.models import TimestampedModel, models


class AnswerCrossCheck(TimestampedModel):
    answer = models.ForeignKey("homework.Answer", on_delete=models.CASCADE)
    checker = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        indexes = [
            Index(fields=["answer", "checker"]),
        ]

        constraints = [
            UniqueConstraint(fields=["answer", "checker"], name="unique_checker_and_answer"),
        ]

    def is_checked(self) -> bool:
        return self.answer.descendants().filter(author=self.checker).exists()
