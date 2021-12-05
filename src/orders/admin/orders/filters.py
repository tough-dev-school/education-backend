from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from app.admin import admin
from orders.models import Order


class OrderStatusFilter(admin.SimpleListFilter):
    title = pgettext_lazy('orders', 'status')
    parameter_name = 'status'

    def lookups(self, *args, **kwargs):
        return [
            ('not_paid', _('Not paid')),
            ('paid', _('Paid')),
            ('shipped_without_payment', _('Shipped without payment')),
        ]

    def queryset(self, request, queryset: QuerySet[Order]):
        """Types are ignored due to https://github.com/typeddjango/django-stubs/issues/353"""
        value = self.value()

        if not value:
            return

        if value == 'not_paid':
            return queryset.paid(invert=True).filter(shipped__isnull=True)  # type: ignore

        if value == 'paid':
            return queryset.paid()  # type: ignore

        if value == 'shipped_without_payment':
            return queryset.shipped_without_payment()  # type: ignore
