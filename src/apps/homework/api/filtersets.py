from django_filters import rest_framework as filters

from apps.homework.models import Answer
from core.api.filters import UUIDInFilter


class AnswerFilterSet(filters.FilterSet):
    question = filters.UUIDFilter(field_name="question__slug")
    author = filters.UUIDFilter(field_name="author__uuid")

    class Meta:
        model = Answer
        fields = [
            "question",
            "author",
        ]


class AnswerCommentFilterSet(filters.FilterSet):
    answer = UUIDInFilter(field_name="slug", required=True)

    class Meta:
        model = Answer
        fields = [
            "answer",
        ]
