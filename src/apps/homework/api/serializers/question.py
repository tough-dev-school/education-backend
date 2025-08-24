from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.api.serializers.stats import HomeworkStatsSerializer
from apps.homework.models import Question
from core.serializers import MarkdownField


class QuestionSerializer(serializers.ModelSerializer):
    text = MarkdownField()
    markdown_text = serializers.CharField(source="text")

    class Meta:
        model = Question
        fields = [
            "slug",
            "name",
            "text",
            "markdown_text",
            "deadline",
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    text = MarkdownField()
    markdown_text = serializers.CharField(source="text")
    breadcrumbs = serializers.SerializerMethodField()
    homework = HomeworkStatsSerializer(source="*")
    course = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "breadcrumbs",
            "slug",
            "name",
            "text",
            "markdown_text",
            "deadline",
            "homework",
            "course",
        ]

    @extend_schema_field(lazy_serializer("apps.lms.api.serializers.LMSCourseSerializer")())
    def get_course(self, question: Question) -> dict:
        from apps.lms.api.serializers import LMSCourseSerializer

        course = question.get_course(user=self.context["request"].user)

        if course is None:
            course = question.get_legacy_course()

        return LMSCourseSerializer(course).data

    @extend_schema_field(lazy_serializer("apps.lms.api.serializers.BreadcrumbsSerializer")())
    def get_breadcrumbs(self, question: Question) -> dict | None:
        from apps.lms.api.serializers import BreadcrumbsSerializer

        lesson = question.get_lesson(user=self.context["request"].user)

        return BreadcrumbsSerializer(lesson).data if lesson is not None else None
