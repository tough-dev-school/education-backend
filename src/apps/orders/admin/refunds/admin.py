from typing import Any

from django.contrib import admin

from apps.orders.models import Refund


class RefundInline(admin.TabularInline):
    can_delete = False
    show_change_link = False
    model = Refund
    fields = ["created", "amount", "author", "bank_id"]

    readonly_fields = [
        "created",
        "amount",
        "author",
        "bank_id",
    ]

    def has_add_permission(self, *args: Any, **kwargs: Any) -> bool:
        return False
