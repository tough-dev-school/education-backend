from typing import TYPE_CHECKING

from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.models import Answer, AnswerCrossCheck, AnswerImage, Question
from apps.homework.models.reaction import Reaction
from apps.users.api.serializers import UserSafeSerializer
from core.serializers import MarkdownField, SoftField

if TYPE_CHECKING:
    from apps.homework.models.answer import AnswerQuerySet


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


class AnswerSerializer(serializers.ModelSerializer):
    author = UserSafeSerializer()
    text = MarkdownField()
    src = serializers.CharField(source="text")
    parent = SoftField(source="parent.slug")  # type: ignore
    question = serializers.CharField(source="question.slug")
    has_descendants = serializers.SerializerMethodField()
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

    def get_descendants_queryset(self, answer: Answer) -> "AnswerQuerySet":
        user = self.context["request"].user
        if user.has_perm("homework.see_all_answers"):
            return answer.get_comments()

        return answer.get_limited_comments_for_user_by_crosschecks(user)

    def get_has_descendants(self, answer: Answer) -> bool:
        if answer.author_id == self.context["request"].user.id:
            return self.get_descendants_queryset(answer).exists()

        return answer.children_count > 0


class AnswerTreeSerializer(AnswerSerializer):
    descendants = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = AnswerSerializer.Meta.fields + [
            "descendants",
        ]

    @extend_schema_field(AnswerSerializer(many=True))
    def get_descendants(self, answer: Answer) -> list[dict]:
        cached = self._get_cached_descendands(answer)
        if cached is not None:
            return cached

        descendants = AnswerTreeSerializer(
            self.get_descendants_queryset(answer).prefetch_reactions().select_related("question", "author", "parent", "parent__parent"),
            many=True,
            context=self.context,
        ).data

        self._answer_descendands_cache = dict()
        self._answer_descendands_cache[answer.id] = descendants

        return descendants  # type: ignore

    def get_has_descendants(self, answer: Answer) -> bool:
        return len(self.get_descendants(answer)) > 0

    def _get_cached_descendands(self, answer: Answer) -> list[dict] | None:
        """LRU cache for descendants

        we call this method twice and want to avoid double query"""
        if not hasattr(self, "_answer_descendands_cache"):
            return None

        cache: dict = self._answer_descendands_cache
        return cache.get(answer.id, None)


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


class AnswerSimpleSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source="get_absolute_url")
    author = UserSafeSerializer()
    question = QuestionSerializer()

    class Meta:
        model = Answer
        fields = ("slug", "url", "author", "question")


class AnswerCrossCheckSerializer(serializers.ModelSerializer):
    answer = AnswerSimpleSerializer()
    is_checked = serializers.SerializerMethodField()

    class Meta:
        model = AnswerCrossCheck
        fields = (
            "answer",
            "is_checked",
        )

    def get_is_checked(self, obj: "AnswerCrossCheck") -> bool:
        return obj.checked is not None
