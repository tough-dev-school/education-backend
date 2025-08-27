from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema_serializer
from rest_framework import serializers

from apps.lms.models import Module
from core.serializers import MarkdownField


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Markdown in descrpition",
            value={
                "id": 100500,
                "name": "Первая неделя",
                "has_started": True,
                "start_date": "2023-12-01 15:30:00+03:00",
                "description": "Cамая важная неделя",
                "text": "<p><strong>Первая</strong> неделя — <em>самая важная неделя</em></p>",
            },
        ),
    ]
)
class ModuleSerializer(serializers.ModelSerializer):
    text = MarkdownField()
    has_started = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "start_date",
            "has_started",
            "description",
            "text",
        ]

    def get_has_started(self, module: Module) -> bool:
        if module.start_date is None:
            return True

        return module.start_date <= timezone.now()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Default",
            value={
                "id": 100500,
                "name": "Первая неделя",
                "has_started": True,
                "start_date": "2023-12-01 15:30:00+03:00",
                "description": "Cамая важная неделя",
                "lesson_count": 1,
                "single_lesson_id": 57,
                "text": "<p><strong>Первая</strong> неделя — <em>самая важная неделя</em></p>",
            },
        ),
        OpenApiExample(
            name="Multiple lessons",
            value={
                "id": 100500,
                "name": "Вторая неделя",
                "has_started": True,
                "start_date": "2023-12-01 15:30:00+03:00",
                "description": "Тоже важная неделя",
                "lesson_count": 2,
                "single_lesson_id": None,
                "text": "<p><strong>Первая</strong> неделя — <em>самая важная неделя</em></p>",
            },
        ),
    ]
)
class ModuleDetailSerializer(ModuleSerializer):
    lesson_count = serializers.IntegerField()  # has to be annotated by .for_viewset()
    single_lesson_id = serializers.IntegerField()

    class Meta(ModuleSerializer.Meta):
        model = Module
        fields = ModuleSerializer.Meta.fields + [
            "lesson_count",
            "single_lesson_id",
        ]
