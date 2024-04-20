from typing import Any

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.orders.admin.refunds.forms import RefundAddForm
from apps.orders.models.order import Order
from apps.orders.models.refund import Refund
from core.admin import TabularInline


class RefundInline(TabularInline):
    form = RefundAddForm
    can_delete = False
    show_change_link = False
    model = Refund
    extra = 0
    fields = ("amount", "created", "bank_id", "author")
    readonly_fields = ("created", "bank_id", "author")
    verbose_name = _("Partial refund")
    verbose_name_plural = _("Partial refunds")

    def has_change_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def has_add_permission(self, request: HttpRequest, obj: "Order") -> bool:  # type: ignore
        return obj.price != 0
