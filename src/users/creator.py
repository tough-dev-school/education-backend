import uuid

from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
        ]


class UserCreator:
    """Service object for creating a user"""
    def __init__(self, name, email):
        self.data = {
            'email': email,
            'username': email or str(uuid.uuid4()),
            **User.parse_name(name),
        }

    def __call__(self) -> User:
        return self.get() or self.create()

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
