from django_filters import rest_framework as filters

from homework.models import Answer


class AnswerFilterSet(filters.FilterSet):
    question = filters.CharFilter(field_name='question__slug')

    class Meta:
        model = Answer
        fields = [
            'question',
        ]
