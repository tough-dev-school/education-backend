import uuid
from dataclasses import dataclass
from django.utils.functional import cached_property
from rest_framework import serializers

from app.integrations.dashamail.helpers import subscribe_user_to_dashamail
from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'subscribed',
        ]


@dataclass
class UserCreator:
    email: str
    name: str | None = ''
    subscribe: bool | None = False
    tags: list[str] | None = None

    @cached_property
    def username(self) -> str:
        return self.email.lower() or str(uuid.uuid4())

    def __call__(self) -> User:
        user = self.get() or self.create()
        self.after_creation(created_user=user)

        return user

    def get(self) -> User | None:
        if self.email:
            return User.objects.filter(is_active=True).filter(email__iexact=self.email).first()

    def create(self) -> User:
        serializer = UserCreateSerializer(data={
            'email': self.email.lower(),
            'username': self.username,
            'subscribed': self.subscribe,
            **User.parse_name(self.name or ''),
        })
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance  # type: ignore

    def after_creation(self, created_user: User) -> None:
        if self.subscribe:
            if created_user.email and len(created_user.email):
                subscribe_user_to_dashamail(user=created_user, tags=self.tags or [])
