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


class DefaultBooleanFilter(admin.SimpleListFilter):
    """Abstract base class for simple boolean filter with default value in admin.
    You should define `title`, unique `parameter_name` and `default_value`. The order
    of elements in the right sidebar should be considered as undefined:
        class IsActiveFilter(DefaultBooleanFilter):
            title = _('Is active')
            parameter_name = 'active'
            default_value = True
    """

    default_value: Optional[bool] = None

    def __init__(self, *args, **kwargs):
        if not isinstance(self.default_value, bool):
            raise NotImplementedError(f"The filter {self.__class__.__name__} does not specify a 'default_value' as a bool.")
        boolean_values = [('f', _('No')), ('t', _('Yes'))]
        self.lookup_values = (
            ('all', _('All')),
            boolean_values[not self.default_value],
            (None, boolean_values[self.default_value][1]),  # take only verbose name for default value.
        )
        return super().__init__(*args, **kwargs)

    def lookups(self, request, model_admin):
        return self.lookup_values

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(**{self.parameter_name: self.default_value})
        elif self.value() == 'all':
            return queryset
        else:
            return queryset.filter(**{self.parameter_name: self.value() == 't'})
