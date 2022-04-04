from typing import Optional

from django.contrib import admin
from django.utils.translation import gettext_lazy as _


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
            def n(self, request, queryset):
                return queryset.filter(classes__isnull=True)
    """
    def lookups(self, request, model_admin):
        return (
            ('t', _('Yes')),
            ('f', _('No')),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        else:
            if self.value() == 't':
                return self.t(request, queryset)
            else:
                return self.f(request, queryset)


class DefaultFilter(admin.SimpleListFilter):
    """Abstract base class for simple filter with a default value in
    admin. You should define `title`, unique `parameter_name`,
    `default_value`, `lookups` and `queryset` methods.
    """
    default_value: Optional[str] = None

    def __init__(self, *args, **kwargs):
        if self.default_value is None:
            raise NotImplementedError(f"The filter {self.__class__.__name__} does not specify a 'default_value'.")
        super().__init__(*args, **kwargs)

    def choices(self, cl):
        """Yields choices from `lookups` and doesn't yield "All" element."""

        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, *args, **kwargs):
        if self.value() is None:
            self.used_parameters[self.parameter_name] = self.default_value
        return super().queryset(*args, **kwargs)


class DefaultBooleanFilter(DefaultFilter, BooleanFilter):
    """Abstract base class for simple boolean filter with default value in
    admin. You should define `title`, unique `parameter_name` and
    `default_value` as "t" or "f":
        class IsActivePromocodeFilter(DefaultBooleanFilter):
            title = _('Active')
            parameter_name = 'active'
            default_value = 't'

            def t(self, request, queryset):
                return queryset.filter(active=True)

            def f(self, request, queryset):
                return queryset.filter(active=False)
    """
