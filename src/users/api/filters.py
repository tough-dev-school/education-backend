from typing import TYPE_CHECKING

from django_filters import rest_framework as filters

from products.models import Course
from users.models import User

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from users.models import UserQuerySet


class UserFilter(filters.FilterSet):
    course = filters.NumberFilter(method="_course")

    class Meta:
        model = User
        fields = ("course",)

    def _course(self, queryset: "UserQuerySet", name: str, value: int) -> "QuerySet":
        del name

        course = Course.objects.filter(pk=value).first()

        return queryset.for_course(course=course) if course else queryset.none()
