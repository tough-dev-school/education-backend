from rest_framework import serializers

from apps.homework.api.serializers.question import QuestionSerializer
from apps.homework.models import Question
from apps.lms.models import Lesson


class CrossCheckStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField(source="crosschecks_total")
    checked = serializers.IntegerField(source="crosschecks_checked")


class CommentStatsSerializer(serializers.Serializer):
    comments = serializers.IntegerField(source="comment_count")
    hidden_before_crosscheck_completed = serializers.SerializerMethodField()

    def get_hidden_before_crosscheck_completed(self, instance: Lesson | Question) -> int | None:
        request = self.context["request"]
        return instance.comment_count - instance.get_allowed_comment_count(request.user)  # hope lesson is annotated

    def to_representation(self, instance: Lesson | Question) -> dict:
        if not instance.is_sent:
            return {}

        return super().to_representation(instance)


class HomeworkStatsSerializer(serializers.Serializer):
    is_sent = serializers.BooleanField()
    crosschecks = CrossCheckStatsSerializer(required=False, source="*")
    comments = CommentStatsSerializer(required=False, source="*")
    question = QuestionSerializer(required=False)
