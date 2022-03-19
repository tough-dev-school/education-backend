from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from chains.admin.forms import MessageAddForm, MessageEditForm
from chains.models import Message


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    add_form = MessageAddForm
    form = MessageEditForm

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
        'course',
        'chain',
        'parent',
        'template_id',
        'delay',
    ]

    list_filter = [
        'chain__course',
        'chain',
    ]

    list_select_related = [
        'parent',
        'chain',
        'chain__course',
    ]

    @admin.display(description=_('Course'), ordering='chain__course')
    def course(self, obj: Message) -> str:
        return str(obj.chain.course)


__all__ = [
    'MessageAdmin',
]
