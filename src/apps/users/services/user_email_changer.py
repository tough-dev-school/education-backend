from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.dashamail import tasks as dashamail
from apps.dashamail.enabled import dashamail_enabled
from apps.users.models import User
from core.services import BaseService


@dataclass
class UserEmailChanger(BaseService):
    user: User
    new_email: str
    force_subscribe: bool | None = False

    def act(self) -> None:
        if not User.objects.filter(email=self.new_email).exists():
            self._check_if_username_is_not_taken(self.new_email)
            self.user.email = self.new_email
            self.user.username = self.new_email
            self.user.save(update_fields=["email", "username"])

            self.user.refresh_from_db()

            self.after_changing()

        else:
            raise NotImplementedError("User merging is not implemented yet")

    def after_changing(self) -> None:
        if self.force_subscribe and dashamail_enabled():
            self.push_to_dashamail(self.user)

    @staticmethod
    def _check_if_username_is_not_taken(username: str) -> None:
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")

    @staticmethod
    def push_to_dashamail(user: User) -> None:
        dashamail.update_subscription.apply_async(
            kwargs={"student_id": user.id},
            countdown=5,  # voodoo sleep to make sure the user table is updated
        )
