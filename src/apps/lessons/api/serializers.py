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


class LessonSerializer(serializers.ModelSerializer):
    material = NotionMaterialSerializer()
    homework = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "material",
            "homework",
        ]

    def get_homework(self, obj: Lesson) -> dict | None:
        if obj.question_id is not None:
            return {
                "is_sent": obj.is_sent,
                "crosschecks": {
                    "total": obj.crosschecks_total,
                    "checked": obj.crosschecks_checked,
                },
            }
