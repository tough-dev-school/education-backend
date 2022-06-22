from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from app.admin.filters import DefaultTrueBooleanFilter
from orders.admin.promocodes import actions
from orders.models import PromoCode


class PromodeActiveFilter(DefaultTrueBooleanFilter):
    title = _('Active')
    parameter_name = 'is_active'

    def t(self, request, queryset):
        return queryset.filter(active=True)

    def f(self, request, queryset):
        return queryset.filter(active=False)


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = (
        'id',
        'name',
        'discount',
        'order_count',
        'comment',
        'active',
    )

    list_editable = [
        'active',
    ]

    list_filter = (
        PromodeActiveFilter,
    )

    list_display_links = (
        'id',
        'name',
    )

    actions = [actions.deactivate]

    def get_queryset(self, request):
        return super().get_queryset(request) \
            .with_order_count()

    @admin.display(description=_('Order count'), ordering='order_count')
    def order_count(self, obj: PromoCode | None = None) -> str:
        if hasattr(obj, 'order_count') and obj.order_count:
            return str(obj.order_count)

        return '—'

    @admin.display(description=_('Discount'), ordering='discount_percent')
    def discount(self, obj: PromoCode | None = None) -> str:
        if not obj:
            return '—'

        if obj.discount_value is not None:
            return f'{obj.discount_value} ₽'

        return f'{obj.discount_percent} %'
