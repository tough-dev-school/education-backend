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


class CrossCheckTask(TimestampedModel):
    source_cross_check = models.ForeignKey("homework.AnswerCrossCheck", on_delete=models.CASCADE, related_name="source_tasks")
    answer = models.ForeignKey("homework.Answer", on_delete=models.CASCADE, related_name="cross_check_tasks")

    required_cross_check = models.ForeignKey("homework.AnswerCrossCheck", on_delete=models.CASCADE, related_name="required_tasks")

    class Meta:
        indexes = [
            Index(fields=["source_cross_check", "answer"]),
        ]

        constraints = [
            UniqueConstraint(fields=["source_cross_check", "answer"], name="unique_source_cross_check_and_answer"),
        ]
