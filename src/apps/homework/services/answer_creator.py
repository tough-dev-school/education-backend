from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

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
        self.check_crosscheck(instance)
        return instance

    def create(self) -> "Answer":
        return Answer.objects.create(**self.data)

    def check_crosscheck(self, instance: "Answer") -> None:
        """
        Do nothing if the parent of the current answer does not exist or if the homework is not crosscheckable.
        """
        if instance.parent:
            AnswerCrossCheck.objects.filter(answer=instance.parent, checker=self.user).update(checked_at=timezone.now())
