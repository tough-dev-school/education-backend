from typing import Any

from django.contrib.admin import SimpleListFilter
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.products.models import Course


class CourseFilter(SimpleListFilter):
    title = _("Course")
    parameter_name = "course_id"

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[Any, str]]:
        queryset = Course.objects.for_admin()

        return [(course.pk, str(course)) for course in queryset.iterator()]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value():
            return queryset

        return queryset.filter(course_id=self.value())


__all__ = [
    "CourseFilter",
]
