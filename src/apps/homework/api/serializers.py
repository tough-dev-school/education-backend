from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.models import Answer, AnswerCrossCheck, AnswerImage, Question
from apps.homework.models.reaction import Reaction
from apps.users.api.serializers import UserSafeSerializer
from core.serializers import MarkdownField, SoftField


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
            "deadline",
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    text = MarkdownField()
    breadcrumbs = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "breadcrumbs",
            "slug",
            "name",
            "text",
            "deadline",
        ]

    @extend_schema_field(lazy_serializer("apps.lms.api.serializers.BreadcrumbsSerializer")())
    def get_breadcrumbs(self, question: Question) -> dict | None:
        from apps.homework.breadcrumbs import get_lesson
        from apps.lms.api.serializers import BreadcrumbsSerializer

        lesson = get_lesson(question, user=self.context["request"].user)
        if lesson is None:
            return None

        return BreadcrumbsSerializer(lesson).data


class AnswerDetailedSerializer(serializers.ModelSerializer):
    author = UserSafeSerializer()
    text = MarkdownField()
    src = serializers.CharField(source="text")
    parent = SoftField(source="parent.slug")  # type: ignore
    question = serializers.CharField(source="question.slug")
    has_descendants = serializers.BooleanField(source="children_count")
    reactions = ReactionDetailedSerializer(many=True)
    is_editable = serializers.BooleanField()

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
            "is_editable",
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

    @extend_schema_field(lazy_serializer("apps.homework.api.serializers.AnswerTreeSerializer")(many=True))
    def get_descendants(self, obj: Answer) -> list[dict]:
        queryset = (
            obj.get_limited_comments_for_user_by_crosschecks(self.context["request"].user)
            .with_children_count()
            .select_related("question", "author", "parent", "parent__parent")
            .prefetch_reactions()
        )

        return AnswerTreeSerializer(  # type: ignore
            queryset,
            many=True,
            context=self.context,
        ).data


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


class AnswerUpdateSerializer(serializers.ModelSerializer):
    """For swagger only"""

    class Meta:
        model = Answer
        fields = [
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
    image = serializers.FileField()

    class Meta:
        model = AnswerImage
        fields = [
            "author",
            "image",
        ]


class SimpleAnswerSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url")
    author = UserSafeSerializer()

    class Meta:
        model = Answer
        fields = ("url", "author")


class AnswerCrossCheckSerializer(serializers.ModelSerializer):
    answer = SimpleAnswerSerializer()
    is_checked = serializers.SerializerMethodField()

    class Meta:
        model = AnswerCrossCheck
        fields = (
            "answer",
            "is_checked",
        )

    def get_is_checked(self, obj: "AnswerCrossCheck") -> bool:
        return obj.checked is not None
