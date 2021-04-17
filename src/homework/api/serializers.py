from rest_framework import serializers

from app.serializers import MarkdownXField, SoftField
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
    parent = SoftField(source='parent.slug')

    class Meta:
        model = Answer
        fields = [
            'slug',
            'author',
            'parent',
            'text',
        ]
