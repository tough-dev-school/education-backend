from rest_framework import serializers

from users.models import User


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
            'gender',
        ]


class UserUpdater:
    def __init__(self, user: User, user_data: dict):
        self.user = user
        self.user_data = user_data

    def __call__(self) -> User:
        user = self.user

        self.update(user)
        user.refresh_from_db()

        return user

    def update(self, user):
        serializer = UserUpdateSerializer(instance=user, data=self.user_data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()
