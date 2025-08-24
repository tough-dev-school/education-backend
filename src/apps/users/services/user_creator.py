import uuid
from dataclasses import dataclass

from django.utils.functional import cached_property
from rest_framework import serializers

from apps.dashamail import tasks as dashamail
from apps.dashamail.enabled import dashamail_enabled
from apps.users.models import User
from core.services import BaseService


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]


@dataclass
class UserCreator(BaseService):
    email: str
    name: str | None = ""
    force_subscribe: bool | None = False

    @cached_property
    def username(self) -> str:
        return self.email.lower() or str(uuid.uuid4())

    def act(self) -> User:
        existing_user = self.get()
        if existing_user is not None:
            return existing_user

        created_user = self.create()

        if self.force_subscribe and dashamail_enabled():
            self.push_to_dashamail(created_user)

        return created_user

    def get(self) -> User | None:
        if self.email:
            return User.objects.filter(is_active=True).filter(email__iexact=self.email).first()

    def create(self) -> User:
        serializer = UserCreateSerializer(
            data={
                "email": self.email.lower(),
                "username": self.username,
                **User.parse_name(self.name or ""),
            }
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance  # type: ignore

    @staticmethod
    def push_to_dashamail(user: User) -> None:
        dashamail.update_subscription.apply_async(
            kwargs={"student_id": user.id},
            countdown=5,  # voodoo sleep to make sure the new row became available in all other transactions
        )
