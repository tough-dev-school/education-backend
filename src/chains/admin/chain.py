from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from app.admin.filters import DefaultFalseBooleanFilter
from chains.models import Chain


class ChainArchivedFilter(DefaultFalseBooleanFilter):
    title = _('Archived')
    parameter_name = 'is_archived'

    def t(self, request, queryset):
        return queryset.archived()

    def f(self, request, queryset):
        return queryset.exclude(
            pk__in=queryset.archived().values_list('pk'),
        )


@admin.register(Chain)
class ChainAdmin(ModelAdmin):
    fields = [
        'name',
        'course',
        'sending_is_active',
        'archived',
    ]

    list_display = [
        'id',
        'name',
        'course',
        'sending_is_active',
        'archived',
    ]

    list_editable = [
        'name',
        'sending_is_active',
        'archived',
    ]

    list_filter = [
        ChainArchivedFilter,
    ]


__all__ = [
    'ChainAdmin',
]
