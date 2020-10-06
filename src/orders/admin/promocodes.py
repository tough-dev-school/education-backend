from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, admin
from orders.models import PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = [
        'id',
        'name',
        'discount_percent',
        'order_count',
        'comment',
        'active',
    ]

    list_editable = [
        'name',
        'discount_percent',
        'active',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .with_order_count()

    def order_count(self, obj=None):
        return obj.order_count if obj and hasattr(obj, 'order_count') and obj.order_count else '—'

    order_count.short_description = _('Order count')
    order_count.admin_order_field = 'order_count'
