from typing import TYPE_CHECKING

from django.http import HttpRequest
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
    ]
    add_form = DealCreateForm
    form = DealChangeForm
    readonly_fields = [
        "author",
    ]
    inlines = [StudentInline]
    actions = [
        actions.complete,
        actions.ship_without_payment,
        actions.cancel,
    ]

    @admin.display(description=_("Status"))
    def status(self, obj: Deal) -> "StrPromise":
        if obj.canceled is not None:
            return pgettext_lazy("deals", "canceled")

        if obj.completed is not None:
            return pgettext_lazy("deals", "complete")

        return pgettext_lazy("deals", "in_progress")

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
