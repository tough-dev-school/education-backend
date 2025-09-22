from dataclasses import dataclass
from core.prosemirror import prosemirror_to_text

from django.db import transaction

from apps.homework.models import Answer
from core.services import BaseService


@dataclass
class AnswerUpdater(BaseService):
    answer: Answer
    content: dict

    @transaction.atomic
    def act(self) -> Answer:
        self.update()

        return self.answer

    def update(self) -> None:
        self.answer.content = self.content
        self.answer.text = prosemirror_to_text(self.content)

        self.answer.save(update_fields=["content", "text", "modified"])
