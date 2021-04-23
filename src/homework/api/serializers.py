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
            'created',
            'slug',
            'author',
            'parent',
            'text',
        ]


class AnswerCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    parent = serializers.SlugRelatedField(slug_field='slug', queryset=Answer.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Answer
        fields = [
            'author',
            'question',
            'parent',
            'text',
        ]
