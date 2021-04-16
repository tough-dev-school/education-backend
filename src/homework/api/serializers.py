from rest_framework import serializers

from app.serializers import MarkdownXField
from homework.models import Answer, Question
from users.api.serializers import UserNameSerializer


class QuestionSerializer(serializers.ModelSerializer):
    text = MarkdownXField()

    class Meta:
        model = Question
        fields = [
            'slug',
            'name',
            'text',
        ]


class AnswerSerializer(serializers.ModelSerializer):
    author = UserNameSerializer()
    text = MarkdownXField()

    class Meta:
        model = Answer
        fields = [
            'slug',
            'author',
            'text',
        ]
