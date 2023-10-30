from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="__str__")

    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "name",
            "username",
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "email",
            "gender",
            "github_username",
            "linkedin_username",
            "telegram_username",
        ]


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "first_name",
            "last_name",
        ]
