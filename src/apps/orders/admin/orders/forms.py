from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order
from apps.orders.services import OrderCourseChanger, OrderCreator
from core.admin import ModelForm


class OrderChangeForm(ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        help_texts = {
            "course": _("User receives new welcome letter"),
        }

    def save(self, commit: bool = True) -> Order:
        order = super().save(commit=commit)

        self.call_services(order)

        return order

    def call_services(self, order: Order) -> None:
        self._change_course_if_required(order)

    def _change_course_if_required(self, order: Order) -> None:
        if self.initial["course"] != self.cleaned_data["course"].pk:
            course_changer = OrderCourseChanger(order=order, course=self.cleaned_data["course"])
            course_changer()


class OrderAddForm(forms.ModelForm):
    author = forms.CharField(required=False, widget=forms.HiddenInput)
    paid = forms.CharField(required=False, widget=forms.HiddenInput)
    shipped = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Order
        fields = "__all__"

    def save(self, commit: bool = True) -> Order:
        order_creator = OrderCreator(
            user=self.cleaned_data["user"],
            item=self.cleaned_data["course"] or self.cleaned_data["bundle"] or self.cleaned_data["record"],
            price=self.cleaned_data["price"],
            desired_bank=self.cleaned_data["bank_id"],
        )

        return order_creator()

    def clean_bank_id(self) -> str:
        if self.cleaned_data["bank_id"]:
            return self.cleaned_data["bank_id"]

        if int(self.cleaned_data["price"] > 0):
            return "b2b"

        return "adhoc"

    def save_m2m(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        """For some weird reason django requires this method to be present"""
