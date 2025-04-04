from django_filters import rest_framework as filters

from apps.lessons.models import Lesson


class LessonFilterSet(filters.FilterSet):
    class Meta:
        model = Lesson
        fields = [
            "module",
        ]
