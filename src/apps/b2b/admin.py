from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.b2b.models import Customer, Deal, Student
from apps.b2b.services import BulkStudentCreator, DealCreator
from core.admin import ModelAdmin, admin


@admin.register(Customer)
class CustomerAdmin(ModelAdmin): ...


class DealCreateForm(forms.ModelForm):
    author = forms.CharField(required=False, widget=forms.HiddenInput)
    students = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Deal
        fields = "__all__"

    def save(self, commit: bool = False) -> Deal:
        deal = DealCreator(
            customer=self.cleaned_data["customer"],
            product=self.cleaned_data["product"],
            price=self.cleaned_data["price"],
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
        deal = super().save(commit=commit)

        student_list = self.cleaned_data["students"]
        if len(student_list) > 0:
            BulkStudentCreator(user_input=student_list, deal=deal)()

        return deal


class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = [
        "name",
        "email",
    ]
    readonly_fields = [
        "name",
        "email",
    ]

    def name(self, obj: Student) -> str:
        return obj.user.get_full_name()

    def email(self, obj: Student) -> str:
        return obj.user.email

    def has_add_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    def has_change_permission(self, request: Any, obj: Any = None) -> bool:
        return False

    class Media:
        css = {
            "all": ("admin/css/condensed_students.css",),
        }


@admin.register(Deal)
class DealAdmin(ModelAdmin):
    fields = [
        "author",
        "customer",
        "product",
        "price",
        "comment",
        "students",
    ]
    add_form = DealCreateForm
    form = DealChangeForm
    readonly_fields = [
        "author",
    ]
    inlines = [StudentInline]
