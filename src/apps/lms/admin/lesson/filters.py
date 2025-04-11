from django.db.models import QuerySet
from django.http import HttpRequest

from apps.products.admin.filters import CourseFilter


class LessonCourseFilter(CourseFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value():
            return queryset

        return queryset.filter(module__course_id=self.value())


__all__ = [
    "LessonCourseFilter",
]
