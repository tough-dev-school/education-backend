from rest_framework import serializers

from app.serializers import MarkdownXField
from homework.models import Question
from products.api.serializers import CourseListSerializer


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
