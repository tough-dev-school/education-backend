from django.utils.translation import gettext_lazy as _

from app.admin.filters import DefaultBooleanFilter


class IsActivePromocodeFilter(DefaultBooleanFilter):
    title = _('Active')
    parameter_name = 'active'
    default_value = 't'

    def t(self, request, queryset):
        return queryset.filter(active=True)

    def f(self, request, queryset):
        return queryset.filter(active=False)
