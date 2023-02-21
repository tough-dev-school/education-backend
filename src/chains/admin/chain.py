from app.admin import ModelAdmin, admin
from chains.models import Chain


@admin.register(Chain)
class ChainAdmin(ModelAdmin):
    fields = [
        'name',
        'course',
        'sending_is_active',
        'is_archived',
    ]

    list_display = [
        'id',
        'name',
        'course',
        'sending_is_active',
        'is_archived',
    ]

    list_editable = [
        'name',
        'sending_is_active',
        'is_archived',
    ]


__all__ = [
    'ChainAdmin',
]
