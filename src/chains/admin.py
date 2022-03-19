from app.admin import ModelAdmin, admin
from chains.models import Chain, Message


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


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    fields = [
        'name',
        'chain',
        'parent',
        'template_id',
        'delay',
    ]

    list_display = [
        'id',
        'name',
        'chain',
        'parent',
        'template_id',
        'delay',
    ]

    list_editable = [
        'name',
        'template_id',
        'delay',
    ]
