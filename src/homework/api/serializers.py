from typing import cast

from rest_framework import serializers

from app.serializers import MarkdownField
from app.serializers import SoftField
from homework.models import Answer
from homework.models import AnswerImage
from homework.models import Question
from homework.models.reaction import Reaction
from users.api.serializers import UserSafeSerializer


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


class QuestionSerializer(serializers.ModelSerializer):
    text = MarkdownField()

    class Meta:
        model = Question
        fields = [
            "slug",
            "name",
            "text",
        ]


class AnswerDetailedSerializer(serializers.ModelSerializer):
    author = UserSafeSerializer()
    text = MarkdownField()
    src = serializers.CharField(source="text")
    parent = SoftField(source="parent.slug")  # type: ignore
    question = serializers.CharField(source="question.slug")
    has_descendants = serializers.BooleanField(source="children_count")
    reactions = ReactionDetailedSerializer(many=True)

    class Meta:
        model = Answer
        fields = [
            "created",
            "modified",
            "slug",
            "question",
            "author",
            "parent",
            "text",
            "src",
            "has_descendants",
            "reactions",
        ]


class AnswerTreeSerializer(AnswerDetailedSerializer):
    descendants = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = [
            "created",
            "modified",
            "slug",
            "question",
            "author",
            "parent",
            "text",
            "src",
            "descendants",
            "has_descendants",
            "reactions",
        ]

    def get_descendants(self, obj: Answer) -> list[dict]:
        queryset = obj.get_first_level_descendants().with_children_count().select_related("question", "author").prefetch_reactions()
        serializer = AnswerTreeSerializer(
            queryset,
            many=True,
            context=self.context,
        )

        return cast(list[dict], serializer.data)


class AnswerCreateSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    parent = serializers.SlugRelatedField(slug_field="slug", queryset=Answer.objects.all(), required=False, allow_null=True)  # type: ignore
    question = serializers.SlugRelatedField(slug_field="slug", queryset=Question.objects.all())

    class Meta:
        model = Answer
        fields = [
            "author",
            "question",
            "parent",
            "text",
        ]


class AnswerCommentTreeSerializer(AnswerTreeSerializer):
    class Meta:
        model = Answer
        fields = [
            "slug",
            "descendants",
        ]


class AnswerImageSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = AnswerImage
        fields = [
            "author",
            "image",
        ]
