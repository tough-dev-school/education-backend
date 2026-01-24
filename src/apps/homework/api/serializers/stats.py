from rest_framework import serializers

from apps.homework.models import Question, StatsAnnotatedQuestion


class CrossCheckStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField(source="crosschecks_total")
    checked = serializers.IntegerField(source="crosschecks_checked")


class CommentStatsSerializer(serializers.Serializer):
    comments = serializers.IntegerField(source="comment_count")
    hidden_before_crosscheck_completed = serializers.SerializerMethodField()

    def get_hidden_before_crosscheck_completed(self, instance: StatsAnnotatedQuestion) -> int | None:
        request = self.context["request"]
        return instance.comment_count - instance.get_allowed_comment_count(request.user)  # type: ignore[attr-defined]

    def to_representation(self, instance: StatsAnnotatedQuestion) -> dict:
        if not instance.is_sent:  # type: ignore[attr-defined]
            return {}

        return super().to_representation(instance)


class TemporarySoonToBeDepricatedQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "slug",
            "name",
            "deadline",
        ]


class HomeworkStatsSerializer(serializers.Serializer):
    """Requires *any* model annotaded with statistics. For annotation examples check homework.QuestionQuerySet"""

    is_sent = serializers.BooleanField()
    crosschecks = CrossCheckStatsSerializer(required=False, source="*")
    comments = CommentStatsSerializer(required=False, source="*")
    question = TemporarySoonToBeDepricatedQuestionSerializer(source="*")
