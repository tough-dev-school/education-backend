from django_filters import rest_framework as filters

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
