import contextlib
from typing import Optional

from django.db.models import Index, QuerySet, UniqueConstraint

from app.models import TimestampedModel, models


class AnswerAccessLogEntryQuerySet(QuerySet):
    def get_for_user_and_answer(self, answer, user) -> Optional['AnswerAccessLogEntry']:
        with contextlib.suppress(self.model.DoesNotExist):
            return self.get(answer=answer, user=user)

        return None


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
