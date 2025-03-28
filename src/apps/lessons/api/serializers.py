from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.homework.models import Question
from apps.lessons.models import Lesson
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


class LessonSerializer(serializers.ModelSerializer):
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
    def get_homework(self, obj: Lesson) -> dict | None:
        if obj.question_id is not None:
            return {
                "is_sent": obj.is_sent,
                "crosschecks": {
                    "total": obj.crosschecks_total,
                    "checked": obj.crosschecks_checked,
                },
            }
