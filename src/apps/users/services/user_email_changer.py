from dataclasses import dataclass

from apps.users.models import User
from core.services import BaseService


@dataclass
class UserEmailChanger(BaseService):
    user: User
    new_email: str

    def act(self) -> None:
        if not User.objects.filter(email=self.new_email).exists():
            self.change_email_for_existing_user()

        else:
            raise NotImplementedError("User merging is not implemented yet")

    def change_email_for_existing_user(self) -> None:
        self.user.email = self.new_email
        self.user.save(update_fields=["email"])
