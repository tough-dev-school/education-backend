from dataclasses import dataclass

from django.db import transaction

from apps.homework.models import Answer, AnswerCrossCheck
from core.services import BaseService


@dataclass
class AnswerRemover(BaseService):
    instance: "Answer"

    @transaction.atomic
    def act(self) -> None:
        if self.should_uncheck():
            self.update_crosscheck_is_checked_state()

        self.instance.delete()

    def should_uncheck(self) -> bool:
        if not self.instance.parent:
            return False

        return not self.instance.parent.descendants().filter(author=self.instance.author).exclude(pk=self.instance.pk).exists()

    def update_crosscheck_is_checked_state(self) -> None:
        AnswerCrossCheck.objects.filter(answer=self.instance.parent, checker=self.instance.author).update(checked_at=None)
