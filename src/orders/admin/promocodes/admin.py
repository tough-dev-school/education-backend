from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from orders.models import PromoCode
from orders.admin.promocodes import actions


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = [
        'id',
        'name',
        'discount_percent',
        'discount_value',
        'order_count',
        'comment',
        'active',
    ]

    list_editable = [
        'active',
    ]

    list_filter = [
        'active',
    ]

    actions = [actions.deactivate]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .with_order_count()

    @mark_safe
    @admin.display(description=_('Order count'), ordering='order_count')
    def order_count(self, obj=None):
        if hasattr(obj, 'order_count') and obj.order_count:
            orders_url = reverse('admin:orders_order_changelist')
            return f'<a href="{orders_url}?is_paid=t&promocode_id={obj.id}">{obj.order_count}</a>'

        return '—'
