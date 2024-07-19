from django_filters import rest_framework as filters

from apps.homework.models import Answer, AnswerCrossCheck
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


class AnswerCrossCheckFilterSet(filters.FilterSet):
    question = UUIDInFilter(field_name="answer__question__slug", required=True)

    class Meta:
        model = AnswerCrossCheck
        fields = [
            "question",
        ]
