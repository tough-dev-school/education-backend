from django_filters import rest_framework as filters

from apps.lms.models import Lesson, Module


class LessonFilterSet(filters.FilterSet):
    class Meta:
        model = Lesson
        fields = [
            "module",
        ]


class ModuleFilterSet(filters.FilterSet):
    class Meta:
        model = Module
        fields = [
            "course",
        ]
