from django.utils.translation import gettext_lazy as _

from app.admin.filters import BooleanFilter


class IsRootFilter(BooleanFilter):
    title = _('Is root answer')
    parameter_name = 'is_root'

    def t(self, request, queryset):
        return queryset.filter(parent__isnull=True)

    def f(self, request, queryset):
        return queryset.filter(parent__isnull=False)
