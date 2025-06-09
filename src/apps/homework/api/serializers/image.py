from rest_framework import serializers

from apps.homework.models import AnswerImage


class AnswerImageSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    image = serializers.FileField()

    class Meta:
        model = AnswerImage
        fields = [
            "author",
            "image",
        ]
