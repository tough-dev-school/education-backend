from typing import cast

from rest_framework import serializers

from app.serializers import MarkdownXField, SoftField
from homework.models import Answer, Question
from users.api.serializers import UserSafeSerializer


class QuestionSerializer(serializers.ModelSerializer):
    text = MarkdownXField()

    class Meta:
        model = Question
        fields = [
            'slug',
            'name',
            'text',
        ]


class AnswerDetailedSerializer(serializers.ModelSerializer):
    author = UserSafeSerializer()
    text = MarkdownXField()
    src = serializers.CharField(source='text')
    parent = SoftField(source='parent.slug')  # type: ignore
    question = serializers.CharField(source='question.slug')
    has_descendants = serializers.BooleanField(source='children_count')

    class Meta:
        model = Answer
        fields = [
            'created',
            'modified',
            'slug',
            'question',
            'author',
            'parent',
            'text',
            'src',
            'has_descendants',
        ]


class AnswerTreeSerializer(AnswerDetailedSerializer):
    descendants = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            'created',
            'modified',
            'slug',
            'question',
            'author',
            'parent',
            'text',
            'src',
            'descendants',
        ]

    def get_descendants(self, obj: Answer) -> list[dict]:
        queryset = obj.get_first_level_descendants()
        serializer = AnswerTreeSerializer(
            queryset,
            many=True,
            context=self.context,
        )

        return cast(list[dict], serializer.data)


class AnswerCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    parent = serializers.SlugRelatedField(slug_field='slug', queryset=Answer.objects.all(), required=False, allow_null=True)  # type: ignore
    question = serializers.SlugRelatedField(slug_field='slug', queryset=Question.objects.all())

    class Meta:
        model = Answer
        fields = [
            'author',
            'question',
            'parent',
            'text',
        ]


class AnswerCommentTreeSerializer(AnswerTreeSerializer):

    class Meta:
        model = Answer
        fields = [
            'slug',
            'descendants',
        ]
