from rest_framework import serializers

from apps.lessons.models import Lesson
from apps.notion.models import Material as NotionMaterial


class NotionMaterialSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug")

    class Meta:
        model = NotionMaterial
        fields = [
            "id",
            "title",
        ]


class LessonSerializer(serializers.ModelSerializer):
    material = NotionMaterialSerializer()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "material",
        ]
