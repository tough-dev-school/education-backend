from typing import Iterable, Optional

import uuid
from rest_framework import serializers

from app.tasks import subscribe_to_mailchimp
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
    def __init__(self, name: str, email: str, subscribe: Optional[bool] = True, tags: Optional[Iterable[str]] = None):
        self.do_subscribe = subscribe
        self.subscribe_tags = tags

        if email is not None:
            email = email.lower()

        self.data = {
            'email': email,
            'username': email or str(uuid.uuid4()),
            'subscribed': subscribe,
            **User.parse_name(name),
        }

    def __call__(self) -> User:
        self.resulting_user = self.get() or self.create()

        self.after_creation()
        return self.resulting_user

    def get(self):
        return User.objects.filter(email=self.data['email']).first()

    def create(self):
        serializer = UserCreateSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance

    def after_creation(self):
        if self.do_subscribe:
            if self.resulting_user.email and len(self.resulting_user.email):
                subscribe_to_mailchimp.delay(user_id=self.resulting_user.pk, tags=self.subscribe_tags)
