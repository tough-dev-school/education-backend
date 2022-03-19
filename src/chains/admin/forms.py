from django import forms

from chains.models import Chain, Message


class ChainChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj: Chain) -> str:  # type: ignore
        return f'{obj.course}, {obj}'


class MessageForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Message.objects.may_be_parent())
    chain = ChainChoiceField(queryset=Chain.objects.editable())

    class Meta:
        model = Message
        fields = '__all__'
