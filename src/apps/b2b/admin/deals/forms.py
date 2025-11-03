from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.b2b.models import Deal
from apps.b2b.services import BulkStudentCreator, DealCreator, DealCurrencyChanger
from core.admin import ModelForm


class DealCreateForm(ModelForm):
    author = forms.CharField(required=False, widget=forms.HiddenInput)
    students = forms.CharField(
        label=_("Students"),
        required=False,
        widget=forms.Textarea,
    )

    class Meta:
        model = Deal
        fields = "__all__"

    def save(self, commit: bool = False) -> Deal:
        deal = DealCreator(
            customer=self.cleaned_data["customer"],
            course=self.cleaned_data["course"],
            price=self.cleaned_data["price"],
            currency=self.cleaned_data["currency"],
        )()

        student_list = self.cleaned_data["students"]
        if len(student_list) > 0:
            BulkStudentCreator(user_input=student_list, deal=deal)()

        return deal

    def save_m2m(self, *args: Any, **kwargs: dict[str, Any]) -> None: ...


class DealChangeForm(forms.ModelForm):
    students = forms.CharField(
        label=_("Bulk students add"),
        help_text=_("For complete deals new students will create new orders"),
        required=False,
        widget=forms.Textarea,
    )

    class Meta:
        model = Deal
        fields = "__all__"

    def save(self, commit: bool = False) -> Deal:
        self._change_currency(deal=self.instance)

        deal = super().save(commit=commit)

        self._create_students(deal)

        return deal

    def _change_currency(self, deal: Deal) -> None:
        currency = self.cleaned_data["currency"]
        if self.initial["currency"] != currency:
            DealCurrencyChanger(deal, new_currency_code=currency)()

    def _create_students(self, deal: Deal) -> None:
        student_list = self.cleaned_data["students"]
        if len(student_list) > 0:
            BulkStudentCreator(user_input=student_list, deal=deal)()
