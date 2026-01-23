import uuid
from dataclasses import dataclass

from django.utils.functional import cached_property
from rest_framework import serializers

from apps.dashamail import tasks as dashamail
from apps.dashamail.enabled import dashamail_enabled
from apps.users.models import User
from apps.users.random_name import random_name
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
            return User.objects.filter(is_active=True).filter(email__iexact=self.email).order_by("date_joined").first()

    def create(self) -> User:
        user = User.objects.create(
            email=self.email.lower(),
            username=self.username,
            random_name=random_name(),
            **User.parse_name(self.name or ""),
        )
        return user

    @staticmethod
    def push_to_dashamail(user: User) -> None:
        dashamail.update_subscription.apply_async(
            kwargs={"student_id": user.id},
            countdown=5,  # voodoo sleep to make sure the new row became available in all other transactions
        )
