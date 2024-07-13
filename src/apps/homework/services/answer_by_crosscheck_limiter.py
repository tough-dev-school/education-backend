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
class AnswerDescendantsByCrossCheckLimiter(BaseService):
    answer: "Answer"
    user: "User"

    def act(self) -> "AnswerQuerySet":
        if self.should_limit():
            return self.queryset[: self.allowed_answers_count]

        return self.queryset

    def should_limit(self) -> bool:
        """
        Make no sense to limit answers if the answer is not mine or the answer is not a first level descendant, because it can't be crosschecked
        """
        root_answer_is_mine = self.answer.get_root_answer().author == self.user
        answer_parent_is_first_level_descendant = getattr(self.answer.parent, "parent", None) is None

        return root_answer_is_mine and answer_parent_is_first_level_descendant

    @cached_property
    def queryset(self) -> "AnswerQuerySet":
        return (
            self.answer.get_first_level_descendants()
            .with_children_count()
            .select_related("question", "author", "parent", "parent__parent")
            .prefetch_reactions()
        )

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
