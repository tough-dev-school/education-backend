from typing import Any

from django import forms

from apps.b2b.models import Customer, Deal
from apps.b2b.services.deal_creator import DealCreator
from core.admin import ModelAdmin, admin


@admin.register(Customer)
class CustomerAdmin(ModelAdmin): ...


class DealCreateForm(forms.ModelForm):
    author = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Deal
        fields = "__all__"

    def save(self, commit: bool = False) -> Deal:
        return DealCreator(
            customer=self.cleaned_data["customer"],
            product=self.cleaned_data["product"],
            price=self.cleaned_data["price"],
        )()

    def save_m2m(self, *args: Any, **kwargs: dict[str, Any]) -> None: ...


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    fields = [
        "author",
        "customer",
        "product",
        "price",
        "comment",
    ]
    add_form = DealCreateForm
    readonly_fields = [
        "author",
    ]
