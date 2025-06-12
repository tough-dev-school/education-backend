from rest_framework import serializers

from apps.homework.models import Reaction
from apps.users.api.serializers import UserSafeSerializer


class ReactionDetailedSerializer(serializers.ModelSerializer):
    author = UserSafeSerializer()
    answer = serializers.CharField(source="answer.slug")

    class Meta:
        model = Reaction
        fields = [
            "slug",
            "emoji",
            "author",
            "answer",
        ]


class ReactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaction
        fields = [
            "emoji",
            "slug",
        ]
