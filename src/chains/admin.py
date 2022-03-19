from django import forms
from django.utils.translation import gettext_lazy as _

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


class MessageForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Message.objects.may_be_parent())

    class Meta:
        model = Message
        fields = '__all__'


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    form = MessageForm
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
