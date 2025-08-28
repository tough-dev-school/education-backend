from drf_spectacular.utils import extend_schema_field, inline_serializer
from rest_framework import serializers

from apps.lms.api.serializers.module import ModuleSerializer
from apps.lms.models import Course, Lesson
from core.serializers import MarkdownField


class LMSCourseSerializer(serializers.ModelSerializer):
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


class BreadcrumbsSerializer(serializers.ModelSerializer):
    module = ModuleSerializer()
    course = LMSCourseSerializer(source="module.course")
    lesson = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "module",
            "course",
            "lesson",
        ]

    @extend_schema_field(
        field=inline_serializer(
            name="LessonPlainSerializer",
            fields={
                "id": serializers.IntegerField(),
            },
        )
    )
    def get_lesson(self, lesson: Lesson) -> dict:
        return {
            "id": lesson.id,
        }
