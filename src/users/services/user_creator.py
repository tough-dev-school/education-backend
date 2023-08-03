from dataclasses import dataclass
import uuid

from celery import chain
from rest_framework import serializers

from django.utils.functional import cached_property

from amocrm.tasks import amocrm_enabled
from amocrm.tasks import push_customer
from app.services import BaseService
from users.models import User
from users.tasks import rebuild_tags


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
        user = self.get() or self.create()
        self.after_creation(created_user=user)

        return user

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

    def after_creation(self, created_user: User) -> None:
        has_email = created_user.email and len(created_user.email)
        if self.subscribe and has_email:
            if amocrm_enabled():
                tasks_chain = chain(
                    rebuild_tags.si(student_id=created_user.id),
                    push_customer.si(user_id=created_user.id).set(queue="amocrm"),
                )
                tasks_chain.delay()
            else:
                rebuild_tags.delay(student_id=created_user.id)
