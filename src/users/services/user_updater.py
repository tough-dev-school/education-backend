from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from diplomas.tasks import regenerate_diplomas
from users.models import User


class UserUpdaterException(ValidationError):
    """Use it if user could not be updated."""


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
            'telegram_username',
        ]


class UserUpdater:
    def __init__(self, user: User, user_data: dict):
        self.user = user
        self.user_data = user_data

    def __call__(self) -> User:
        self.validate_socials()

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

    def validate_socials(self) -> None:
        social_fields = ['linkedin_username', 'github_username', 'telegram_username']

        filter_query = Q()

        for social in social_fields:
            if self.user_data.get(social):
                filter_query |= Q(**{social: self.user_data.get(social)})

        if filter_query and User.objects.exclude(pk=self.user.pk).filter(filter_query).exists():
            raise UserUpdaterException(detail={'serviceError': 'One or several social usernames are used by another user.'})
