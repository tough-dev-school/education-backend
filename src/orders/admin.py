from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, admin
from app.admin.filters import BooleanFilter
from orders.models import Order


class OrderPaidFilter(BooleanFilter):
    title = _('Is paid')
    parameter_name = 'is_paid'

    def t(self, request, queryset):
        return queryset.paid()

    def f(self, request, queryset):
        return queryset.paid(invert=True)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        'id',
        'created',
        'customer',
        'item',
        'is_paid',
    ]
    list_display_links = [
        'id',
        'created',
    ]

    list_filter = [
        OrderPaidFilter,
    ]

    def customer(self, obj):
        return str(obj.user)

    customer.short_description = _('User')
    customer.admin_order_field = ('user__id')

    def item(self, obj):
        return obj.item.name

    item.short_description = _('Item')

    def is_paid(self, obj):
        if obj.paid is not None:
            return _('Paid')

        return _('Not paid')

    is_paid.short_description = _('Is paid')
    is_paid.admin_order_field = 'paid'
