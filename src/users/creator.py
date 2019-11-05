from rest_framework import serializers

from users.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]


class UserCreator:
    """Service object for creating a user"""
    def __init__(self, name, email):
        self.data = {
            'email': email,
            **User.parse_name(name),
        }

    def __call__(self):
        serializer = UserCreateSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance
