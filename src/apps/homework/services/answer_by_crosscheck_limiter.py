from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.db.models import Count, Q
from django.utils.functional import cached_property

from core.services import BaseService

if TYPE_CHECKING:
    from apps.homework.models import Answer
    from apps.homework.models.answer import AnswerQuerySet
    from apps.users.models import User


@dataclass
class AnswerByCrossCheckLimiter(BaseService):
    answer: "Answer"
    user: "User"
    queryset: "AnswerQuerySet"

    def act(self) -> "AnswerQuerySet":
        return self.queryset[: self.allowed_answers_count]

    @cached_property
    def answers_count(self) -> int:
        return self.queryset.count()

    @cached_property
    def allowed_answers_count(self) -> int:
        data = self.user.answercrosscheck_set.filter(answer__question=self.answer.question).aggregate(
            checked=Count("pk", filter=Q(checked_at__isnull=False)), total=Count("pk")
        )

        if data["total"] > data["checked"]:
            return data["checked"]

        return self.answers_count
