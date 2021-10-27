from django import forms
from django.utils.translation import gettext_lazy as _

from orders.models import Order
from orders.services import OrderEmailChanger


class OrderChangeForm(forms.ModelForm):
    email = forms.CharField(help_text=_('If changed user, receives welcome letter one more time'))

    class Meta:
        model = Order
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        order = kwargs['instance']
        initial = kwargs.get('initial') or dict()

        if order is not None:
            initial.update(self.get_custom_initial_data(order))

        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_custom_initial_data(order: Order) -> dict:
        return {
            'email': order.user.email,
        }

    def save(self, commit=True) -> Order:
        order = super().save(commit=commit)

        self.call_services(order)

        return order

    def call_services(self, order):
        self._change_email_if_required(order)

    def _change_email_if_required(self, order: Order):
        if self.initial['email'] != self.cleaned_data['email']:
            email_changer = OrderEmailChanger(order=order, email=self.cleaned_data['email'])
            email_changer()
