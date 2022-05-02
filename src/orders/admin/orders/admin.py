from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from orders.admin.orders import actions
from orders.admin.orders.filters import OrderStatusFilter
from orders.admin.orders.forms import OrderAddForm, OrderChangeForm
from orders.models import Order
from users.models import Student


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    form = OrderChangeForm
    add_form = OrderAddForm
    list_display = [
        'id',
        'date',
        'customer',
        'item',
        'is_paid',
        'promocode',
    ]
    list_display_links = [
        'id',
        'date',
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
        actions.generate_diplams,
    ]
    readonly_fields = [
        'author',
        'login_as',
        'paid',
        'shipped',
        'unpaid',
    ]

    fieldsets = [
        (
            None,
            {
                'fields': ['user', 'price', 'email', 'author', 'login_as', 'paid', 'shipped', 'unpaid'],
            },
        ),
        (
            _('Item'),
            {
                'fields': ['course', 'record', 'bundle'],
            },
        ),
    ]

    @property
    def media(self):
        media = super().media

        media._css_lists.append({'all': ['admin/order_list.css']})

        return media

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user',
            'record',
            'course',
        )

    @admin.display(description=_('Date'), ordering='created__id')
    def date(self, obj: Order):
        return obj.created.strftime('%d.%m.%Y')

    @admin.display(description=_('User'), ordering='user__id')
    def customer(self, obj: Order):
        name_template = '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;'
        name = str(obj.user)
        email = obj.user.email

        total_length = len(name) + len(email)

        if 30 <= total_length <= 34:
            return format_html(
                name_template,
                name=obj.user.first_name,
                email=email,
            )
        elif total_length > 34:
            return format_html(
                '<a href="mailto:{email}">{email}</a>',
                email=email,
            )
        else:
            return format_html(
                '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;',
                name=name,
                email=email,
            )

    @admin.display(description=_('Item'))
    def item(self, obj):
        return obj.item.name if obj.item is not None else '—'

    @admin.display(description=_('Is paid'), ordering='paid')
    def is_paid(self, obj: Order):
        if obj.paid is not None:
            return _('Yes')

        if obj.shipped is not None:
            return _('Shipped without payment')

        return _('No')

    @admin.display(description=_('Login as customer'))
    @mark_safe
    def login_as(self, obj: Order) -> str:
        if obj.pk is None:
            return '—'

        login_as_url = Student.objects.get(pk=obj.user_id).get_absolute_url()

        return f'<a href="{login_as_url}" target="_blank">Зайти от имени студента</a>'

    def has_pay_permission(self, request):
        return request.user.has_perm('orders.pay_order')

    def has_unpay_permission(self, request):
        return request.user.has_perm('orders.unpay_order')
