from django import forms

from chains.models import Chain, Message


class ChainChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: Chain) -> str:  # type: ignore
        return f'{obj.course}, {obj}'


class MessageAddForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Message.objects.may_be_parent())
    chain = ChainChoiceField(queryset=Chain.objects.editable())

    class Meta:
        model = Message
        fields = '__all__'

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/limit_message_choices.js',
            'admin/js/clickable_message_intervals.js',
        )


class MessageEditForm(forms.ModelForm):
    chain = ChainChoiceField(queryset=Chain.objects.all())

    class Meta:
        model = Message
        fields = '__all__'

    class Media:
        js = (
            'admin/js/vendor/jquery/jquery.js',
            'admin/js/limit_message_choices.js',
            'admin/js/clickable_message_intervals.js',
        )


__all__ = [
    'MessageEditForm',
    'MessageAddForm',
]
