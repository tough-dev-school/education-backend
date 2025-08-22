import contextlib
from dataclasses import dataclass
from typing import Callable

from django.db import transaction
from django.utils import timezone
from django.utils.functional import cached_property
from rest_framework.exceptions import NotAuthenticated, NotFound, ValidationError

from apps.homework.models import Answer, Question
from apps.studying.models import Study
from apps.users.models import User
from core.current_user import get_current_user
from core.helpers import is_valid_uuid
from core.services import BaseService


@dataclass
class AnswerCreator(BaseService):
    text: str
    content: dict
    question_slug: str
    parent_slug: str | None = None

    @transaction.atomic
    def act(self) -> Answer:
        instance = self.create()

        if self.is_answer_to_crosscheck(instance):
            self.complete_crosscheck(instance)

        return instance

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_question_slug,
            self.validate_parent_slug,
            self.validate_json_or_text,
        ]

    def create(self) -> Answer:
        return Answer.objects.create(
            parent=self.parent,
            question=self.question,
            author=self.author,
            study=self.study,
            text=self.text,
            content=self.content,
        )

    @cached_property
    def author(self) -> User:
        user = get_current_user()
        if user is None:
            raise NotAuthenticated()

        return user

    @cached_property
    def parent(self) -> Answer | None:
        if self.parent_slug is None or len(self.parent_slug) == 0:
            return None

        with contextlib.suppress(Answer.DoesNotExist):
            return Answer.objects.get(slug=self.parent_slug)

    @cached_property
    def question(self) -> Question:
        try:
            return Question.objects.for_user(
                self.author,
            ).get(
                slug=self.question_slug,
            )

        except Question.DoesNotExist:
            raise NotFound()

    @cached_property
    def study(self) -> Study | None:
        """Find the study record of a student to the given course.
        No record means its is the answer from expert or one of us"""
        course = self.question.get_course(user=self.author)
        with contextlib.suppress(Study.DoesNotExist):
            return Study.objects.get(course=course, student=self.author)

    def is_answer_to_crosscheck(self, instance: Answer) -> bool:
        if instance.parent is None:
            return False

        return instance.parent.answercrosscheck_set.filter(checker=self.author).exists()

    def complete_crosscheck(self, instance: Answer) -> None:
        instance.parent.answercrosscheck_set.filter(checker=self.author).update(checked=timezone.now())

    def validate_json_or_text(self) -> None:
        """Remove it after frontend migration"""
        if self.text is None or len(self.text) == 0:  # validating json
            if not isinstance(self.content, dict) or not len(self.content.keys()):
                raise ValidationError("Please provide text or content field")

    def validate_question_slug(self) -> None:
        """Validate only format, database validation is performed later"""
        if not is_valid_uuid(self.question_slug):
            raise ValidationError("Question should be a valid uuid")

    def validate_parent_slug(self) -> None:
        if self.parent_slug is None or not len(self.parent_slug):  # adding a root answer
            return

        if not is_valid_uuid(self.parent_slug):
            raise ValidationError("Question should be a valid uuid")

        if not Answer.objects.filter(slug=self.parent_slug).exists():
            raise ValidationError("Answer does not exist")
