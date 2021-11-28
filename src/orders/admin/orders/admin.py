from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from orders.admin.orders import actions
from orders.admin.orders.filters import OrderStatusFilter
from orders.admin.orders.forms import OrderAddForm, OrderChangeForm
from orders.models import Order


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    form = OrderChangeForm
    add_form = OrderAddForm
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
        OrderStatusFilter,
        'course',
    ]
    search_fields = [
        'id',
        'course__name',
        'record__course__name',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]
    actions = [
        actions.set_paid,
        actions.ship_without_payment,
        actions.set_not_paid,
        actions.ship_again_if_paid,
        actions.accept_homework,
        actions.disaccept_homework,
    ]
    readonly_fields = [
        'author',
        'paid',
        'shipped',
        'unpaid',
    ]

    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'price', 'email', 'author', 'paid', 'shipped', 'unpaid'],
            },
        ),
        (
            _('Item'),
            {
                'fields': ['course', 'record', 'bundle'],
            },
        ),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'record',
            'course',
        )

    @admin.display(description=_('User'), ordering='user__id')
    def customer(self, obj):
        return format_html(
            '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;',
            name=str(obj.user),
            email=obj.user.email,
        )

    @admin.display(description=_('Item'))
    def item(self, obj):
        return obj.item.name if obj.item is not None else '—'

    @admin.display(description=_('Is paid'), ordering='paid')
    def is_paid(self, obj: Order):
        if obj.paid is not None:
            return _('Paid')

        if obj.shipped is not None:
            return _('Shipped without payment')

        return _('Not paid')

    def has_pay_permission(self, request):
        return request.user.has_perm('orders.pay_order')

    def has_unpay_permission(self, request):
        return request.user.has_perm('orders.unpay_order')
