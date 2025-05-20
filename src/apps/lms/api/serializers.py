from drf_spectacular.utils import extend_schema_field, inline_serializer
from rest_framework import serializers

from apps.homework.api.serializers import QuestionSerializer
from apps.homework.models import Question
from apps.lms.models import Call, Course, Lesson, Module
from apps.notion.models import Material as NotionMaterial


class NotionMaterialSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="get_short_slug")

    class Meta:
        model = NotionMaterial
        fields = [
            "id",
            "title",
        ]


class CallSerializr(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = [
            "name",
            "url",
        ]


class HomeworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "is_sent",
        ]


class CrosscheckStatsSerializer(serializers.Serializer):  # for docs only
    total = serializers.IntegerField()
    checked = serializers.IntegerField()


class HomeworkStatsSerializer(serializers.Serializer):  # for docs only
    is_sent = serializers.BooleanField()
    crosschecks = CrosscheckStatsSerializer(required=False)
    question = QuestionSerializer()


class LessonForUserSerializer(serializers.ModelSerializer):
    """Serialize lesson for the user, lesson should be annotated with crosschecks stats"""

    material = NotionMaterialSerializer(required=False)
    call = CallSerializr(required=False)
    homework = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "material",
            "homework",
            "call",
        ]

    @extend_schema_field(field=HomeworkStatsSerializer)
    def get_homework(self, lesson: Lesson) -> dict | None:
        if lesson.question is not None:
            return {
                "is_sent": lesson.is_sent,
                "question": QuestionSerializer(lesson.question).data,
                "crosschecks": {
                    "total": lesson.crosschecks_total,
                    "checked": lesson.crosschecks_checked,
                },
            }


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            "id",
            "name",
        ]


class LMSCourseSerializer(serializers.ModelSerializer):
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
