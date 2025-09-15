from django.db.models import Q, QuerySet
from django.http import HttpRequest

from apps.products.admin.filters import CourseFilter
from core.admin.filters import ArchivedFilter


class LessonCourseFilter(CourseFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value():
            return queryset

        return queryset.filter(module__course_id=self.value())


class LessonArchivedFilter(ArchivedFilter):
    """Hides archived models by default"""

    def t(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        return queryset.filter(Q(question__archived=True) | Q(module__archived=True))

    def f(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        return queryset.filter(Q(question__isnull=True, module__archived=False) | Q(question__archived=False))


__all__ = [
    "LessonCourseFilter",
]
