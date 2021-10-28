from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from diplomas.models import DiplomaTemplate
from orders.admin.orders.filters import OrderPaidFilter
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
        OrderPaidFilter,
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
        'set_paid',
        'set_not_paid',
        'ship_again_if_paid',
        'generate_diplomas',
    ]
    readonly_fields = [
        'paid',
        'shipped',
        'unpaid',
    ]

    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'price', 'email', 'paid', 'shipped', 'unpaid'],
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
    def is_paid(self, obj):
        if obj.paid is not None:
            return _('Paid')

        return _('Not paid')

    @admin.action(description=_('Set paid'), permissions=['pay'])
    def set_paid(self, request, queryset):
        for order in queryset.iterator():
            order.set_paid()

        self.message_user(request, f'{queryset.count()} orders set as paid')

    @admin.action(description=_('Set not paid'), permissions=['unpay'])
    def set_not_paid(self, request, queryset):
        for order in queryset.iterator():
            order.set_not_paid()

        self.message_user(request, f'{queryset.count()} orders set as not paid')

    @admin.action(description=_('Ship again if paid'))
    def ship_again_if_paid(self, request, queryset):
        shipped_count = 0

        for order in queryset.iterator():
            if order.paid is not None:
                order.ship(silent=True)
                shipped_count += 1

        if shipped_count:
            self.message_user(request, f'{shipped_count} orders shipped again')

    @admin.action(description=_('Generate diplomas'))
    def generate_diplomas(self, request, queryset):
        templates_count = 0

        for order in queryset.iterator():
            for template in DiplomaTemplate.objects.filter(course=order.course):
                template.generate_diploma(student=order.user)
                templates_count += 1

        if templates_count:
            self.message_user(request, f'{templates_count} diplomas generation started')

    def has_pay_permission(self, request):
        return request.user.has_perm('orders.pay_order')

    def has_unpay_permission(self, request):
        return request.user.has_perm('orders.unpay_order')
