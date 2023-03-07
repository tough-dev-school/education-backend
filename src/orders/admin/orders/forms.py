from django import forms
from django.utils.translation import gettext_lazy as _

from orders.models import Order
from orders.services import OrderCreator
from orders.services import OrderEmailChanger


class OrderChangeForm(forms.ModelForm):
    email = forms.CharField(help_text=_("If changed user, receives welcome letter one more time"))

    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        order = kwargs["instance"]
        initial = kwargs.get("initial") or dict()

        if order is not None:
            initial.update(self.get_custom_initial_data(order))

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

    @staticmethod
    def get_custom_initial_data(order: Order) -> dict:
        return {
            "email": order.user.email,
        }

    def save(self, commit=True) -> Order:
        order = super().save(commit=commit)

        self.call_services(order)

        return order

    def call_services(self, order: Order) -> None:
        self._change_email_if_required(order)

    def _change_email_if_required(self, order: Order):
        if self.initial["email"] != self.cleaned_data["email"]:
            email_changer = OrderEmailChanger(order=order, email=self.cleaned_data["email"])
            email_changer()


class OrderAddForm(forms.ModelForm):
    email = forms.CharField(required=False, widget=forms.HiddenInput)
    author = forms.CharField(required=False, widget=forms.HiddenInput)
    paid = forms.CharField(required=False, widget=forms.HiddenInput)
    shipped = forms.CharField(required=False, widget=forms.HiddenInput)
    unpaid = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Order
        fields = "__all__"

    def save(self, commit=True):
        order_creator = OrderCreator(
            user=self.cleaned_data["user"],
            item=self.cleaned_data["course"] or self.cleaned_data["bundle"] or self.cleaned_data["record"],
            price=self.cleaned_data["price"],
        )

        return order_creator()

    def save_m2m(self, *args, **kwargs):
        """For some weird reason django requires this method to be present"""
