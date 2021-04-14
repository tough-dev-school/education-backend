from rest_framework import serializers

from app.serializers import MarkdownXField
from homework.models import Answer, Question
from products.api.serializers import CourseListSerializer
from users.api.serializers import UserNameSerializer


class QuestionSerializer(serializers.ModelSerializer):
    course = CourseListSerializer()
    text = MarkdownXField()

    class Meta:
        model = Question
        fields = [
            'course',
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
