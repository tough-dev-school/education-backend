from typing import Literal

from drf_spectacular.utils import OpenApiExample, extend_schema_field, extend_schema_serializer, inline_serializer
from rest_framework import serializers

from apps.homework.api.serializers import HomeworkStatsSerializer, QuestionSerializer
from apps.homework.models import Question
from apps.lms.models import Call, Course, Lesson, Module
from apps.notion.models import Material as NotionMaterial
from core.serializers import MarkdownField


class NotionMaterialSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="get_short_slug")

    class Meta:
        model = NotionMaterial
        fields = [
            "id",
            "title",
        ]


class CallSerializer(serializers.ModelSerializer):
    video = serializers.SerializerMethodField()
    recommended_video_provider = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = [
            "name",
            "description",
            "url",
            "video",
            "datetime",
            "recommended_video_provider",
        ]

    @extend_schema_field(
        field=inline_serializer(
            name="VideoProviderSerializer",
            fields={
                "provider": serializers.CharField(),
                "embed": serializers.URLField(),
                "src": serializers.URLField(),
            },
            many=True,
        ),
    )
    def get_video(self, call: Call) -> list[dict]:
        videos = []

        if call.youtube_id:
            videos.append(
                {
                    "provider": "youtube",
                    "embed": call.get_youtube_embed_src(),
                    "src": call.get_youtube_url(),
                }
            )

        if call.rutube_id:
            videos.append(
                {
                    "provider": "rutube",
                    "embed": call.get_rutube_embed_src(),
                    "src": call.get_rutube_url(),
                }
            )

        return videos

    def get_recommended_video_provider(self, call: Call) -> Literal["youtube", "rutube"] | None:
        request = self.context["request"]
        if request is not None and request.country_code == "RU" and call.rutube_id is not None:
            return "rutube"

        if call.youtube_id is None and call.rutube_id is not None:
            return "rutube"

        if call.youtube_id is not None:
            return "youtube"

        return None


class LessonSerializer(serializers.ModelSerializer):
    """Serialize lesson for the user, lesson should be annotated with crosschecks stats"""

    material = NotionMaterialSerializer(required=False)
    call = CallSerializer(required=False)
    homework = serializers.SerializerMethodField()
    question = QuestionSerializer()

    class Meta:
        model = Lesson
        fields = [
            "id",
            "material",
            "homework",
            "question",
            "call",
        ]

    @extend_schema_field(field=HomeworkStatsSerializer)
    def get_homework(self, lesson: Lesson) -> dict | None:
        if lesson.question is not None:
            user = self.context["request"].user
            question = Question.objects.for_user(user).get(pk=lesson.question_id)  # extra N+1 query to annotate the question with statistics

            return HomeworkStatsSerializer(question, context=self.context).data


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Markdown in descrpition",
            value={
                "id": 100500,
                "name": "Первая неделя",
                "start_date": "2023-12-01 15:30:00+03:00",
                "description": "Cамая важная неделя",
                "text": "<p><strong>Первая</strong> неделя — <em>самая важная неделя</em></p>",
            },
        ),
    ]
)
class ModuleSerializer(serializers.ModelSerializer):
    text = MarkdownField()

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "start_date",
            "description",
            "text",
        ]


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="Default",
            value={
                "id": 100500,
                "name": "Первая неделя",
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
