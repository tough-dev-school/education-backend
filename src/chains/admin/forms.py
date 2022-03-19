from django import forms

from chains.models import Message


class MessageForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Message.objects.may_be_parent())

    class Meta:
        model = Message
        fields = '__all__'
