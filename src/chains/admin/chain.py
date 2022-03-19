from app.admin import ModelAdmin, admin
from chains.models import Chain


@admin.register(Chain)
class ChainAdmin(ModelAdmin):
    fields = [
        'name',
        'course',
        'sending_is_active',
    ]

    list_display = [
        'id',
        'name',
        'course',
        'sending_is_active',
    ]

    list_editable = [
        'name',
        'sending_is_active',
    ]


__all__ = [
    'ChainAdmin',
]
