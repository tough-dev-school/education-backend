from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from apps.homework.models import Answer
from apps.users.models import User
from core.services import BaseService


@dataclass
class AnswerCreator(BaseService):
    data: dict
    user: "User"

    @transaction.atomic
    def act(self) -> "Answer":
        instance = self.create()

        if self.should_check_crosscheck(instance):
            self.check_crosscheck(instance)

        return instance

    def create(self) -> "Answer":
        return Answer.objects.create(**self.data)

    def should_check_crosscheck(self, instance: "Answer") -> bool:
        if instance.parent is None:
            return False

        return instance.parent.answercrosscheck_set.filter(checker=self.user).exists()

    def check_crosscheck(self, instance: "Answer") -> None:
        instance.parent.answercrosscheck_set.filter(checker=self.user).update(checked_at=timezone.now())
