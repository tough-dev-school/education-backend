from drf_spectacular.helpers import lazy_serializer
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.api.serializers.stats import HomeworkStatsSerializer
from apps.homework.models import Question
from apps.products.models import Course
from core.serializers import MarkdownField


class QuestionCourseSerializer(serializers.ModelSerializer):
    homework_check_recommendations = MarkdownField()

    class Meta:
        model = Course
        fields = [
            "id",
            "slug",
            "name",
            "cover",
            "chat",
            "calendar_ios",
            "calendar_google",
            "homework_check_recommendations",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    markdown_text = serializers.CharField(source="text")

    class Meta:
        model = Question
        fields = [
            "slug",
            "name",
            "markdown_text",
            "deadline",
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
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
            "markdown_text",
            "deadline",
            "homework",
            "course",
        ]

    @extend_schema_field(QuestionCourseSerializer)
    def get_course(self, question: Question) -> dict:
        course = question.get_course(user=self.context["request"].user)

        if course is None:
            course = question.get_legacy_course()

        return QuestionCourseSerializer(course).data

    @extend_schema_field(lazy_serializer("apps.lms.api.serializers.BreadcrumbsSerializer")())
    def get_breadcrumbs(self, question: Question) -> dict | None:
        from apps.lms.api.serializers import BreadcrumbsSerializer

        lesson = question.get_lesson(user=self.context["request"].user)

        return BreadcrumbsSerializer(lesson).data if lesson is not None else None
