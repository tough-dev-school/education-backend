from rest_framework import serializers

from apps.homework.models import Answer, Question
from apps.lessons.models import Lesson
from apps.notion.models import Material as NotionMaterial
from core.current_user import get_current_user


class NotionMaterialSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="get_short_slug")

    class Meta:
        model = NotionMaterial
        fields = [
            "id",
            "title",
        ]


class HomeworkSerializer(serializers.ModelSerializer):
    is_sent = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "is_sent",
        ]

    def get_is_sent(self, obj: Question) -> bool:
        user = get_current_user()
        if user is None:
            return False

        return Answer.objects.root_only().filter(author=user, question=obj).exists()


class LessonSerializer(serializers.ModelSerializer):
    material = NotionMaterialSerializer()
    homework = HomeworkSerializer(source="question")

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "material",
            "homework",
        ]
