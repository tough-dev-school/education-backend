from django.utils.translation import ugettext_lazy as _

from app.admin import admin
from diplomas.models import DiplomaTemplate


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
def generate_diplomas(modeladmin, request, queryset):
    templates_count = 0

    for order in queryset.iterator():
        for template in DiplomaTemplate.objects.filter(course=order.course):
            template.generate_diploma(student=order.user)
            templates_count += 1

    if templates_count:
        modeladmin.message_user(request, f'{templates_count} diplomas generation started')
