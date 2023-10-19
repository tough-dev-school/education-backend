from typing import Any

from django.contrib import admin
from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext as _


class BooleanFilter(admin.SimpleListFilter):
    """
    Abstract base class for simple boolean filter in admin. You should define only
    `title`, unique `parameter_name` and two methods: `t` and `f`, returning a queryset
    when filter is set to True and False respectively:
        class HasClassesFilter(BooleanFilter):
            title = _('Has classes')
            parameter_name = 'has_classes'
            def t(self, request, queryset):
                return queryset.filter(classes__isnull=False).distinct('pk')
            def f(self, request, queryset):
                return queryset.filter(classes__isnull=True)
    """

    def lookups(self, request: HttpRequest, model_admin: Any) -> list[tuple[Any, str]]:
        return [
            ("t", _("Yes")),
            ("f", _("No")),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value():
            return queryset

        if self.value() == "t":
            return self.t(request, queryset)  # type: ignore

        return self.f(request, queryset)  # type: ignore


class DefaultTrueBooleanFilter(BooleanFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value() or self.value() == "t":
            return self.t(request, queryset)  # type: ignore

        return self.f(request, queryset)  # type: ignore


class DefaultFalseBooleanFilter(BooleanFilter):
    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        if not self.value() or self.value() == "f":
            return self.f(request, queryset)  # type: ignore

        return self.t(request, queryset)  # type: ignore


__all__ = [
    "BooleanFilter",
    "DefaultTrueBooleanFilter",
]
