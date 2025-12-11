from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.api.serializers.question import QuestionSerializer
from apps.homework.api.serializers.reaction import ReactionDetailedSerializer
from apps.homework.models import Answer, Question
from apps.homework.models.answer import AnswerQuerySet
from apps.users.api.serializers import UserSafeSerializer
from core.serializers import MarkdownField, SoftField


class AnswerSerializer(serializers.ModelSerializer):
    author = UserSafeSerializer()
    legacy_text = MarkdownField()
    parent = SoftField(source="parent.slug")  # type: ignore
    question = serializers.CharField(source="question.slug")
    has_descendants = serializers.SerializerMethodField()
    reactions = ReactionDetailedSerializer(many=True)
    is_editable = serializers.SerializerMethodField()
    content = serializers.DictField(required=True)

    class Meta:
        model = Answer
        fields = [
            "created",
            "modified",
            "slug",
            "question",
            "author",
            "parent",
            "legacy_text",
            "content",
            "has_descendants",
            "is_editable",
            "reactions",
        ]

    def get_is_editable(self, answer: Answer) -> bool:
        return answer.is_editable and self.context["request"].user == answer.author

    def get_descendants_queryset(self, answer: Answer) -> AnswerQuerySet:
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
            "content",
        ]


class AnswerUpdateSerializer(serializers.ModelSerializer):
    content = serializers.DictField(required=True)

    class Meta:
        model = Answer
        fields = [
            "content",
        ]


class AnswerCommentTreeSerializer(AnswerTreeSerializer):
    class Meta:
        model = Answer
        fields = [
            "slug",
            "descendants",
        ]


class AnswerSimpleSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source="get_absolute_url")
    author = UserSafeSerializer()
    question = QuestionSerializer()

    class Meta:
        model = Answer
        fields = ("slug", "url", "author", "question")
