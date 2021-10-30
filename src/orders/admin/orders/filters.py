from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from app.admin import admin
from orders.models.order import OrderQuerySet


class OrderStatusFilter(admin.SimpleListFilter):
    title = pgettext_lazy('orders', 'status')
    parameter_name = 'status'

    def lookups(self, *args, **kwargs):
        return [
            ('not_paid', _('Not paid')),
            ('paid', _('Paid')),
            ('shipped_without_payment', _('Shipped without payment')),
        ]

    def queryset(self, request, queryset: OrderQuerySet):
        value = self.value()

        if not value:
            return

        if value == 'not_paid':
            return queryset.paid(invert=True).filter(shipped__isnull=True)

        if value == 'paid':
            return queryset.paid()

        if value == 'shipped_without_payment':
            return queryset.shipped_without_payment()
