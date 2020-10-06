from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, action, admin, field
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
        'promocode',
    ]
    list_display_links = [
        'id',
        'created',
    ]

    list_filter = [
        'course',
        'record',
        OrderPaidFilter,
    ]
    search_fields = [
        'course__name',
        'record__course__name',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]
    actions = [
        'set_paid',
        'set_not_paid',
        'ship_again_if_paid',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'record',
            'course',
        )

    @field(short_description=_('User'), admin_order_field='user__id')
    def customer(self, obj):
        return format_html(
            '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;',
            name=str(obj.user),
            email=obj.user.email,
        )

    @field(short_description=_('Item'))
    def item(self, obj):
        return obj.item.name if obj.item is not None else '—'

    @field(short_description=_('Is paid'), admin_order_field='paid')
    def is_paid(self, obj):
        if obj.paid is not None:
            return _('Paid')

        return _('Not paid')

    @action(short_description=_('Set paid'))
    def set_paid(self, request, queryset):
        for order in queryset.iterator():
            order.set_paid()

        self.message_user(request, f'{queryset.count()} orders set as paid')

    @action(short_description=_('Set not paid'))
    def set_not_paid(self, request, queryset):
        queryset.update(shipped=None, paid=None)

        self.message_user(request, f'{queryset.count()} orders set as not paid')

    @action(short_description=_('Ship again if paid'))
    def ship_again_if_paid(self, request, queryset):
        for order in queryset.iterator():
            if order.paid is not None:
                order.ship(silent=True)
