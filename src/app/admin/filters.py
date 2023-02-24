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
            def f(self, request, queryset):
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

        if self.value() == 't':
            return self.t(request, queryset)

        return self.f(request, queryset)


class DefaultTrueBooleanFilter(BooleanFilter):
    def queryset(self, request, queryset):
        if not self.value() or self.value() == 't':
            return self.t(request, queryset)

        return self.f(request, queryset)


class DefaultFalseBooleanFilter(BooleanFilter):
    def queryset(self, request, queryset):
        if not self.value() or self.value() == 'f':
            return self.f(request, queryset)

        return self.t(request, queryset)


__all__ = [
    'BooleanFilter',
    'DefaultTrueBooleanFilter',
]
