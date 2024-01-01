from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order
from apps.orders.services import OrderCourseChanger
from apps.orders.services import OrderCreator
from apps.orders.services import OrderEmailChanger


class OrderChangeForm(forms.ModelForm):
    email = forms.CharField(label=_("Email"), help_text=_("User receives new welcome letter"))

    class Meta:
        model = Order
        fields = "__all__"
        help_texts = {
            "course": _("User receives new welcome letter"),
        }

    def __init__(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        order = kwargs["instance"]
        initial = kwargs.get("initial") or dict()

        if order is not None:
            initial.update(self.get_custom_initial_data(order))  # type: ignore

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)  # type: ignore

    @staticmethod
    def get_custom_initial_data(order: Order) -> dict:
        return {
            "email": order.user.email,
        }

    def save(self, commit: bool = True) -> Order:
        order = super().save(commit=commit)

        self.call_services(order)

        return order

    def call_services(self, order: Order) -> None:
        self._change_email_if_required(order)
        self._change_course_if_required(order)

    def _change_email_if_required(self, order: Order) -> None:
        if self.initial["email"] != self.cleaned_data["email"]:
            email_changer = OrderEmailChanger(order=order, email=self.cleaned_data["email"])
            email_changer()

    def _change_course_if_required(self, order: Order) -> None:
        if self.initial["course"] != self.cleaned_data["course"].pk:
            course_changer = OrderCourseChanger(order=order, course=self.cleaned_data["course"])
            course_changer()


class OrderAddForm(forms.ModelForm):
    email = forms.CharField(required=False, widget=forms.HiddenInput)
    author = forms.CharField(required=False, widget=forms.HiddenInput)
    paid = forms.CharField(required=False, widget=forms.HiddenInput)
    shipped = forms.CharField(required=False, widget=forms.HiddenInput)
    unpaid = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Order
        fields = "__all__"

    def save(self, commit: bool = True) -> Order:
        order_creator = OrderCreator(
            user=self.cleaned_data["user"],
            item=self.cleaned_data["course"] or self.cleaned_data["bundle"] or self.cleaned_data["record"],
            price=self.cleaned_data["price"],
        )

        return order_creator()

    def save_m2m(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        """For some weird reason django requires this method to be present"""
