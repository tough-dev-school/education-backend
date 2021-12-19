from typing import Optional

import contextlib
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _


class AnswerAccessLogEntryQuerySet(QuerySet):
    def get_for_user_and_answer(self, answer, user) -> Optional['AnswerAccessLogEntry']:
        with contextlib.suppress(self.model.DoesNotExist):
            return self.get(answer=answer, user=user)

        return None
