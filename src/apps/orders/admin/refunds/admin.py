from typing import Any

from apps.orders.admin.refunds.forms import RefundAddForm
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

    def has_change_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False
