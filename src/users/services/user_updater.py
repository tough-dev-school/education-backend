from rest_framework import serializers

from diplomas.tasks import regenerate_diplomas
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
            'github_username',
            'linkedin_username',
        ]


class UserUpdater:
    def __init__(self, user: User, user_data: dict):
        self.user = user
        self.user_data = user_data

    def __call__(self) -> User:
        user = self.user

        self.update(user)
        user.refresh_from_db()

        self.after_update()

        return user

    def update(self, user: User) -> None:
        serializer = UserUpdateSerializer(instance=user, data=self.user_data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save()

    def after_update(self) -> None:
        self.regenerate_diplomas()

    def regenerate_diplomas(self) -> None:
        regenerate_diplomas.delay(student_id=self.user.id)
