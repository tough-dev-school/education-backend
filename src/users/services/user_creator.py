from typing import Iterable, Optional

import uuid
from rest_framework import serializers

from app.tasks import subscribe_to_dashamail
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


class UserCreator:
    """Service object for creating a user"""
    def __init__(self, email: str, name: Optional[str] = None, subscribe: Optional[bool] = True, tags: Optional[Iterable[str]] = None):
        self.do_subscribe = subscribe
        self.subscribe_tags = tags

        email = email.lower()

        self.data = {
            'email': email,
            'username': email or str(uuid.uuid4()),
            'subscribed': subscribe,
            **User.parse_name(name or ''),
        }

    def __call__(self) -> User:
        self.resulting_user = self.get() or self.create()

        self.after_creation()
        return self.resulting_user

    def get(self) -> Optional[User]:
        return User.objects.filter(is_active=True).filter(email=self.data['email']).first()

    def create(self) -> User:
        serializer = UserCreateSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance  # type: ignore

    def after_creation(self) -> None:
        if self.do_subscribe:
            if self.resulting_user.email and len(self.resulting_user.email):
                subscribe_to_dashamail.delay(user_id=self.resulting_user.pk, tags=self.subscribe_tags)
