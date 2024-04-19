from django import forms

from apps.orders.models.refund import Refund
from apps.orders.services import OrderRefunder


class RefundAddForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = "__all__"

    def save(self, commit: bool = True) -> Refund:
        order_refunder = OrderRefunder(order=self.cleaned_data["order"], amount=self.cleaned_data["amount"])
        return order_refunder()
