from django_filters import rest_framework as filters

from apps.lessons.models import Lesson


class LessonFilterSet(filters.FilterSet):
    course = filters.CharFilter(field_name="course__slug")

    class Meta:
        model = Lesson
        fields = [
            "course",
        ]
