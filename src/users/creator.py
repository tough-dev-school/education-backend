import uuid

from django.conf import settings
from rest_framework import serializers

from app.tasks import subscribe_to_mailjet
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

    def __init__(self, name, email, subscribe=True):
        self.do_subscribe = subscribe

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
        try:
            return User.objects.get(email=self.data['email'])
        except User.DoesNotExist:
            pass

    def create(self):
        serializer = UserCreateSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance

    def after_creation(self):
        if self.do_subscribe:
            if self.resulting_user.email and len(self.resulting_user.email):
                subscribe_to_mailjet.delay(user_id=self.resulting_user.pk, list_id=settings.MAILJET_LIST_ID_WHERE_ALL_CONTACTS_ARE_STORED)
