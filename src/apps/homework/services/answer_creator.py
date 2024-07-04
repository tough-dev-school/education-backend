from dataclasses import dataclass

from django.db import transaction

from apps.homework.models import Answer, AnswerCrossCheck
from apps.users.models import User
from core.services import BaseService


@dataclass
class AnswerCreator(BaseService):
    data: dict
    user: "User"

    @transaction.atomic
    def act(self) -> "Answer":
        instance = self.create()
        self.update_crosscheck_is_checked_state(instance)
        return instance

    def create(self) -> "Answer":
        return Answer.objects.create(**self.data)

    def update_crosscheck_is_checked_state(self, instance: "Answer") -> None:
        if instance.parent:
            AnswerCrossCheck.objects.filter(answer=instance.parent, checker=self.user).update(is_checked=True)
