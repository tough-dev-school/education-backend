from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.users.models import User
from core.services import BaseService


@dataclass
class UserEmailChanger(BaseService):
    user: User
    new_email: str

    def act(self) -> None:
        if not User.objects.filter(email=self.new_email).exists():
            self._check_if_username_is_not_taken(self.new_email)
            self.user.email = self.new_email
            self.user.username = self.new_email
            self.user.save(update_fields=["email", "username"])

        else:
            raise NotImplementedError("User merging is not implemented yet")

    @staticmethod
    def _check_if_username_is_not_taken(username: str) -> None:
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")
