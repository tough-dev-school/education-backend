from django.utils.translation import gettext_lazy as _

from app.admin.filters import BooleanFilter


class OrderPaidFilter(BooleanFilter):
    title = _('Is paid')
    parameter_name = 'is_paid'

    def t(self, request, queryset):
        return queryset.paid()

    def f(self, request, queryset):
        return queryset.paid(invert=True)
