import uuid
from dataclasses import dataclass

from django.utils.functional import cached_property
from rest_framework import serializers

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
            "subscribed",
        ]


@dataclass
class UserCreator(BaseService):
    email: str
    name: str | None = ""
    subscribe: bool | None = False

    @cached_property
    def username(self) -> str:
        return self.email.lower() or str(uuid.uuid4())

    def act(self) -> User:
        return self.get() or self.create()

    def get(self) -> User | None:
        if self.email:
            return User.objects.filter(is_active=True).filter(email__iexact=self.email).first()

    def create(self) -> User:
        serializer = UserCreateSerializer(
            data={
                "email": self.email.lower(),
                "username": self.username,
                "subscribed": self.subscribe,
                **User.parse_name(self.name or ""),
            }
        )
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance  # type: ignore
