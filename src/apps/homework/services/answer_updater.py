from dataclasses import dataclass

from django.db import transaction

from apps.homework.models import Answer
from core.services import BaseService


@dataclass
class AnswerUpdater(BaseService):
    answer: Answer
    content: dict

    @transaction.atomic
    def act(self) -> Answer:
        self.update_content()

        return self.answer

    def update_content(self) -> None:
        self.answer.content = self.content
        self.answer.save(update_fields=["content", "modified"])
