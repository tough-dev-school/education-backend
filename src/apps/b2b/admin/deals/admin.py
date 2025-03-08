from typing import no_type_check

from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.b2b.admin.deals import actions
from apps.b2b.admin.deals.forms import DealChangeForm, DealCreateForm
from apps.b2b.admin.students import StudentInline
from apps.b2b.models import Deal
from core.admin import ModelAdmin, admin


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    list_display = [
        "customer",
        "price",
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

    @no_type_check
    @admin.display(description=_("Status"))
    def status(self, obj: Deal) -> str:
        if obj.canceled is not None:
            return pgettext_lazy("deals", "canceled")

        if obj.completed is not None:
            return pgettext_lazy("deals", "complete")

        return pgettext_lazy("deals", "in_progress")

    def get_readonly_fields(self, request: HttpRequest, obj: Deal | None = None) -> list[str] | tuple[str, ...]:
        """Block changes for complete and canceled deals"""
        if obj is None or (obj.canceled is None and obj.completed is None):
            return super().get_readonly_fields(request, obj)

        return [
            *super().get_readonly_fields(request, obj),
            "customer",
            "course",
            "price",
        ]
