from typing import TYPE_CHECKING

from django.http import HttpRequest
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.b2b.admin.deals import actions
from apps.b2b.admin.deals.forms import DealChangeForm, DealCreateForm
from apps.b2b.admin.students import StudentInline
from apps.b2b.models import Deal
from core.admin import ModelAdmin, admin

if TYPE_CHECKING:
    from django_stubs_ext import StrPromise


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    list_display = [
        "customer",
        "price_formatted",
        "orders",
        "status",
        "author",
    ]
    fields = [
        "author",
        "customer",
        "course",
        "price",
        "comment",
        "students",
        "orders",
    ]
    add_form = DealCreateForm
    form = DealChangeForm
    readonly_fields = [
        "author",
        "orders",
    ]
    inlines = [StudentInline]
    actions = [
        actions.complete,
        actions.ship_without_payment,
        actions.cancel,
    ]

    @mark_safe
    @admin.display(description=pgettext_lazy("deals", "Orders"))
    def orders(self, obj: Deal) -> str:
        url = reverse("admin:orders_order_changelist") + f"?deal__id__exact={obj.pk}"

        orders_count = obj.orders.count()

        if orders_count == 0:
            return "—"

        return f"<a target='_blank' href='{url}'>{orders_count}</a>"

    @admin.display(description=_("Status"))
    def status(self, obj: Deal) -> "StrPromise":
        return obj.get_status_representation()

    @admin.display(description=_("Price"), ordering="price")
    def price_formatted(self, obj: Deal) -> str:
        return self._price(obj.price)

    def get_readonly_fields(self, request: HttpRequest, obj: Deal | None = None) -> list[str]:
        """Block changes for complete and canceled deals"""
        if obj is None or (obj.canceled is None and obj.completed is None):
            return list(super().get_readonly_fields(request, obj))

        return [
            *super().get_readonly_fields(request, obj),
            "customer",
            "course",
            "price",
        ]
