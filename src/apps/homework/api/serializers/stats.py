from rest_framework import serializers

from apps.homework.models import Question


class CrossCheckStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField(source="crosschecks_total")
    checked = serializers.IntegerField(source="crosschecks_checked")


class CommentStatsSerializer(serializers.Serializer):
    comments = serializers.IntegerField(source="comment_count")
    hidden_before_crosscheck_completed = serializers.SerializerMethodField()

    def get_hidden_before_crosscheck_completed(self, instance: Question) -> int | None:
        request = self.context["request"]
        return instance.comment_count - instance.get_allowed_comment_count(request.user)  # hope the model is annotated

    def to_representation(self, instance: Question) -> dict:
        if not instance.is_sent:
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
