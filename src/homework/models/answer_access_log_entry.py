from django.db.models import Index, UniqueConstraint

from app.models import TimestampedModel, models
from homework.querysets import AnswerAccessLogEntryQuerySet


class AnswerAccessLogEntry(TimestampedModel):
    objects = models.Manager.from_queryset(AnswerAccessLogEntryQuerySet)()

    answer = models.ForeignKey('homework.Answer', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            Index(fields=['answer', 'user']),
        ]
        constraints = [
            UniqueConstraint(fields=['answer', 'user'], name='unique_user_and_answer'),
        ]
