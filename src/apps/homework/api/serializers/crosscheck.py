from rest_framework import serializers

from apps.homework.api.serializers.answer import AnswerSimpleSerializer
from apps.homework.models import AnswerCrossCheck


class CrossCheckSerializer(serializers.ModelSerializer):
    answer = AnswerSimpleSerializer()
    is_checked = serializers.SerializerMethodField()

    class Meta:
        model = AnswerCrossCheck
        fields = (
            "answer",
            "is_checked",
        )

    def get_is_checked(self, obj: "AnswerCrossCheck") -> bool:
        return obj.checked is not None
