from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.b2b.services import DealCompleter
from core.admin import admin


@admin.action(description=_("Complete the deal"))
def complete(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    queryset = queryset.filter(completed__isnull=True, canceled__isnull=True)
    deal_count = queryset.count()

    for deal in queryset.iterator():
        DealCompleter(deal)()

    modeladmin.message_user(request, f"{deal_count} deals complete")


@admin.action(description=_("Ship without payment"))
def ship_without_payment(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    queryset = queryset.filter(completed__isnull=True, canceled__isnull=True)
    deal_count = queryset.count()

    for deal in queryset.iterator():
        DealCompleter(deal=deal, ship_only=True)()

    modeladmin.message_user(request, f"{deal_count} deals shipped without payment")


@admin.action(description=_("Cancel the deal"))
def cancel(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    queryset = queryset.filter(completed__isnull=True, canceled__isnull=True)
    deal_count = queryset.count()

    queryset.update(canceled=timezone.now())

    modeladmin.message_user(request, f"{deal_count} deals canceled")
