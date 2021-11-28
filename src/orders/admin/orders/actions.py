from django.utils.translation import gettext_lazy as _

from app.admin import admin
from orders import tasks
from studying.models import Study


@admin.action(description=_('Set paid'), permissions=['pay'])
def set_paid(modeladmin, request, queryset):
    for order in queryset.iterator():
        order.set_paid()

    modeladmin.message_user(request, f'{queryset.count()} orders set as paid')


@admin.action(description=_('Set not paid'), permissions=['unpay'])
def set_not_paid(modeladmin, request, queryset):
    for order in queryset.iterator():
        order.set_not_paid()

    modeladmin.message_user(request, f'{queryset.count()} orders set as not paid')


@admin.action(description=_('Ship without payments'), permissions=['pay'])
def ship_without_payment(modeladmin, request, queryset):
    shipped_count = 0

    for order in queryset.iterator():
        if order.ship_without_payment():
            shipped_count += 1

    modeladmin.message_user(request, f'{shipped_count} orders shipped')


@admin.action(description=_('Ship again if paid'))
def ship_again_if_paid(modeladmin, request, queryset):
    shipped_count = 0

    for order in queryset.iterator():
        if order.paid is not None:
            order.ship(silent=True)
            shipped_count += 1

    if shipped_count:
        modeladmin.message_user(request, f'{shipped_count} orders shipped again')


@admin.action(description=_('Generate diplomas'))
def generate_diplams(modeladmin, request, queryset):
    order_ids = queryset.values_list('order_id', flat=True)
    tasks.generate_diploma.chunk(order_ids, 10).apply_async()

    modeladmin.message_user(f'Started generation of {len(order_ids)} diplomas')


@admin.action(description=_('Accept homework'))
def accept_homework(modeladmin, request, queryset):
    studies = Study.objects.filter(order__in=queryset)

    studies.update(homework_accepted=True)

    modeladmin.message_user(request, f'{studies.count()} homeworks accepted')


@admin.action(description=_('Disaccept homework'))
def disaccept_homework(modeladmin, request, queryset):
    studies = Study.objects.filter(order__in=queryset)

    studies.update(homework_accepted=True)

    modeladmin.message_user(request, f'{studies.count()} homeworks disaccepted')
