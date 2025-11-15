from dataclasses import dataclass

from django.core.exceptions import ValidationError

from apps.dashamail import tasks as dashamail
from apps.dashamail.enabled import dashamail_enabled
from apps.users.models import User
from apps.users.services.user_data_migrator import UserDataMigrator
from core.services import BaseService


@dataclass
class UserEmailChanger(BaseService):
    """Change user email

    This is ADMIN-ONLY service, which may loose data when migrating them between students with same emails. DO NOT ALLOW END-USERS to use this service
    """

    user: User
    new_email: str

    def act(self) -> None:
        resulting_user = None
        if not User.objects.filter(email=self.new_email).exists():
            resulting_user = self.change_email_to_the_new_one()
            self.after_changing(resulting_user)
        else:
            self.change_email_to_existing()

    def change_email_to_the_new_one(self) -> User:
        """Simple email changing"""
        self._check_if_username_is_not_taken(self.new_email)
        user = self.user

        user.email = self.new_email
        user.username = self.new_email
        user.save(update_fields=["email", "username"])

        return user

    def change_email_to_existing(self) -> None:
        """Migrate current user data to existing user with the same email"""
        destination = User.objects.get(email=self.new_email)
        UserDataMigrator(
            source=self.user,
            destination=destination,
        )()

    @classmethod
    def after_changing(cls, resulting_user: User) -> None:
        if dashamail_enabled():
            cls.push_to_dashamail(resulting_user)

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
