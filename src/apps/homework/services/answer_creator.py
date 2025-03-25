import contextlib
from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.exceptions import NotAuthenticated

from apps.homework.models import Answer, Question
from apps.users.models import User
from core.current_user import get_current_user
from core.helpers import is_valid_uuid
from core.services import BaseService


@dataclass
class AnswerCreator(BaseService):
    text: str
    question_slug: str
    parent_slug: str | None = None

    @transaction.atomic
    def act(self) -> Answer:
        instance = self.create()

        if self.is_answer_to_crosscheck(instance):
            self.complete_crosscheck(instance)

        return instance

    def create(self) -> Answer:
        return Answer.objects.create(
            parent=self._get_parent(),
            question=self._get_question(),
            author=self.author,
            text=self.text,
        )

    @cached_property
    def author(self) -> User:
        user = get_current_user()
        if user is None:
            raise NotAuthenticated()

        return user

    def _get_parent(self) -> Answer | None:
        if not is_valid_uuid(self.parent_slug):
            return None

        with contextlib.suppress(Answer.DoesNotExist):
            return Answer.objects.get(slug=self.parent_slug)

    def _get_question(self) -> Question:
        return Question.objects.get(slug=self.question_slug)

    def is_answer_to_crosscheck(self, instance: Answer) -> bool:
        if instance.parent is None:
            return False

        return instance.parent.answercrosscheck_set.filter(checker=self.author).exists()

    def complete_crosscheck(self, instance: Answer) -> None:
        instance.parent.answercrosscheck_set.filter(checker=self.author).update(checked_at=timezone.now())
