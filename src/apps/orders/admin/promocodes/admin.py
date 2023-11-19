from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.request import Request

from apps.orders.admin.promocodes import actions
from apps.orders.models import PromoCode
from apps.orders.models.promocode import PromoCodeQuerySet
from core.admin import ModelAdmin, admin
from core.admin.filters import DefaultTrueBooleanFilter


class PromodeActiveFilter(DefaultTrueBooleanFilter):
    title = _("Active")
    parameter_name = "is_active"

    def t(self, request: Request, queryset: PromoCodeQuerySet) -> QuerySet:
        return queryset.active()

    def f(self, request: Request, queryset: PromoCodeQuerySet) -> QuerySet:
        return queryset.exclude(
            pk__in=queryset.active().values_list("pk"),
        )


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = (
        "id",
        "name",
        "discount",
        "order_count",
        "destination",
        "is_active",
    )

    list_filter = (PromodeActiveFilter,)

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "destination",
    )

    actions = [actions.deactivate]

    def get_queryset(self, request: Request) -> QuerySet:  # type: ignore
        return super().get_queryset(request).with_order_count()  # type: ignore

    @admin.display(description=_("Order count"), ordering="order_count")
    def order_count(self, obj: PromoCode | None = None) -> str:
        if obj is not None and hasattr(obj, "order_count") and obj.order_count:
            return str(obj.order_count)

        return "—"

    @admin.display(description=_("Discount"), ordering="discount_percent")
    def discount(self, obj: PromoCode | None = None) -> str:
        if not obj:
            return "—"

        if obj.discount_value is not None:
            return f"{obj.discount_value} ₽"

        return f"{obj.discount_percent} %"

    @admin.display(description=_("Active"), boolean=True)
    def is_active(self, obj: PromoCode | None = None) -> bool | None:
        if not obj:
            return None

        if obj.active is True:
            if obj.expires is None or obj.expires >= timezone.now():
                return True

        return False
