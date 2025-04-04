from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.api.serializers import QuestionSerializer
from apps.homework.models import Question
from apps.lms.models import Lesson, Module
from apps.notion.models import Material as NotionMaterial


class NotionMaterialSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="get_short_slug")

    class Meta:
        model = NotionMaterial
        fields = [
            "id",
            "title",
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
    homework = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "material",
            "homework",
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
            "lessons_count",
        ]
