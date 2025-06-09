from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.api.serializers.stats import HomeworkStatsSerializer
from apps.homework.models import Question
from core.serializers import MarkdownField


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
    homework = HomeworkStatsSerializer(source="*")

    class Meta:
        model = Question
        fields = [
            "breadcrumbs",
            "slug",
            "name",
            "text",
            "deadline",
            "homework",
        ]

    @extend_schema_field(lazy_serializer("apps.lms.api.serializers.BreadcrumbsSerializer")())
    def get_breadcrumbs(self, question: Question) -> dict | None:
        from apps.homework.breadcrumbs import get_lesson
        from apps.lms.api.serializers import BreadcrumbsSerializer

        lesson = get_lesson(question, user=self.context["request"].user)
        if lesson is None:
            return None

        return BreadcrumbsSerializer(lesson).data
