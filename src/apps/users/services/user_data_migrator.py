from dataclasses import dataclass

from django.apps import apps
from django.contrib.admin.models import CHANGE
from django.db import transaction
from rest_framework.exceptions import NotAuthenticated

from apps.users.models import User
from core.current_user import get_current_user
from core.services import BaseService
from core.tasks import write_admin_log


@dataclass
class UserDataMigrator(BaseService):
    """Migrates all relevant user data. Used for <user merging> story"""

    source: User
    destination: User

    @transaction.atomic
    def act(self) -> None:
        self.update_orders()
        self.update_studies()
        self.update_homework()

        self.write_auditlog()

    def update_orders(self) -> None:
        apps.get_model("orders.Order").objects.filter(user=self.source).update(
            user=self.destination,
        )

    def update_studies(self) -> None:
        apps.get_model("studying.Study").objects.filter(student=self.source).update(
            student=self.destination,
        )

    def update_homework(self) -> None:
        for model in ["homework.Answer", "homework.AnswerImage", "homework.Reaction"]:
            apps.get_model(model).objects.filter(
                author=self.source,
            ).update(
                author=self.destination,
            )

        apps.get_model("homework.AnswerCrossCheck").objects.filter(checker=self.source).update(
            checker=self.destination,
        )

    def write_auditlog(self) -> None:
        """Write a LogEntry for source and destination user"""
        user = get_current_user()
        if user is None:
            raise NotAuthenticated()

        write_admin_log.delay(
            action_flag=CHANGE,
            change_message=f"User data moved to user #{self.destination.pk}",
            model="users.User",
            object_id=self.source.id,
            user_id=user.id,
        )

        write_admin_log.delay(
            action_flag=CHANGE,
            change_message=f"User data moved from user #{self.source.pk}",
            model="users.User",
            object_id=self.destination.id,
            user_id=user.id,
        )
