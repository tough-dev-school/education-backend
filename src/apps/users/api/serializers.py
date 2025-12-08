from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "username",
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "random_name",
            "email",
            "gender",
            "github_username",
            "linkedin_username",
            "telegram_username",
            "avatar",
        ]


class UserSelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "uuid",
            "username",
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "random_name",
            "email",
            "gender",
            "github_username",
            "linkedin_username",
            "telegram_username",
            "avatar",
            "is_staff",
            "rank",
            "rank_label_color",
        ]


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "gender",
            "github_username",
            "linkedin_username",
            "telegram_username",
            "avatar",
        ]


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "uuid",
            "first_name",
            "last_name",
            "first_name_en",
            "last_name_en",
            "random_name",
            "avatar",
            "rank",
            "rank_label_color",
        ]
