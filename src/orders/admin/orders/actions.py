from typing import Any

from celery import group

from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext as _

from app.admin import admin
from orders import tasks
from studying.models import Study


@admin.action(description=_("Set paid"), permissions=["pay"])
def set_paid(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    for order in queryset.iterator():
        order.set_paid()

    modeladmin.message_user(request, f"{queryset.count()} orders set as paid")


@admin.action(description=_("Refund"), permissions=["unpay"])
def refund(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    for order in queryset.iterator():
        order.refund()

    modeladmin.message_user(request, f"{queryset.count()} orders refunded")


@admin.action(description=_("Ship without payments"), permissions=["pay"])
def ship_without_payment(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    shipped_count = 0

    for order in queryset.iterator():
        if order.ship_without_payment():
            shipped_count += 1

    modeladmin.message_user(request, f"{shipped_count} orders shipped")


@admin.action(description=_("Ship again if paid"))
def ship_again_if_paid(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    shipped_count = 0

    for order in queryset.iterator():
        if order.paid is not None:
            order.ship(silent=True)
            shipped_count += 1

    if shipped_count:
        modeladmin.message_user(request, f"{shipped_count} orders shipped again")


@admin.action(description=_("Generate diplomas"))
def generate_diplomas(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    order_ids = queryset.values_list("id", flat=True)

    generate_diplomas = group([tasks.generate_diploma.s(order_id=order_id) for order_id in queryset.values_list("id", flat=True)])
    generate_diplomas.skew(step=2).apply_async()

    modeladmin.message_user(request, f"Started generation of {len(order_ids)} diplomas")


@admin.action(description=_("Accept homework"))
def accept_homework(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    studies = Study.objects.filter(order__in=queryset)

    studies.update(homework_accepted=True)

    modeladmin.message_user(request, f"{studies.count()} homeworks accepted")


@admin.action(description=_("Disaccept homework"))
def disaccept_homework(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    studies = Study.objects.filter(order__in=queryset)

    studies.update(homework_accepted=True)

    modeladmin.message_user(request, f"{studies.count()} homeworks disaccepted")
