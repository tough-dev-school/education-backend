from django_filters import rest_framework as filters

from app.api.filters import UUIDInFilter
from homework.models import Answer


class AnswerFilterSet(filters.FilterSet):
    question = filters.UUIDFilter(field_name='question__slug')
    author = filters.UUIDFilter(field_name='author__uuid')

    class Meta:
        model = Answer
        fields = [
            'question',
            'author',
        ]


class AnswerCommentFilterSet(filters.FilterSet):
    answer = UUIDInFilter(field_name='slug', required=True)

    class Meta:
        model = Answer
        fields = [
            'answer',
        ]
