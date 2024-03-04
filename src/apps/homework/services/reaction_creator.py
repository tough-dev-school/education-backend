import uuid
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from emoji import is_emoji

from apps.homework.models import Answer
from apps.homework.models.reaction import Reaction
from apps.users.models import User
from core.exceptions import AppServiceException
from core.services import BaseService


class ReactionCreatorException(AppServiceException):
    """Raises when it's impossible to create reaction"""


@dataclass
class ReactionCreator(BaseService):
    emoji: str
    author: User
    answer: Answer
    slug: UUID | None = None

    def act(self) -> Reaction:
        return self.create_reaction(self.emoji, self.author, self.answer)

    def create_reaction(self, emoji: str, author: User, answer: Answer) -> Reaction:
        try:
            return Reaction.objects.create(
                emoji=emoji,
                author=author,
                answer=answer,
                slug=self.slug if self.slug is not None else uuid.uuid4(),
            )
        except IntegrityError as e:
            raise ReactionCreatorException(_(str(e)))

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_is_emoji,
            self.validate_reach_limit,
        ]

    def validate_is_emoji(self) -> None:
        if not is_emoji(self.emoji):
            raise ReactionCreatorException(_("Invalid emoji symbol"))

    def validate_reach_limit(self) -> None:
        authors_reactions_this_answer_count = Reaction.objects.filter(author=self.author, answer=self.answer).count()
        if authors_reactions_this_answer_count >= Reaction.MAX_REACTIONS_FROM_ONE_AUTHOR:
            raise ReactionCreatorException(_(f"Only {Reaction.MAX_REACTIONS_FROM_ONE_AUTHOR} reactions per answer are allowed from one author."))
