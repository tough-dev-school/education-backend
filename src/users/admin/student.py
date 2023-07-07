from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin
from users.models import Student
from users.models import User
from users.services import UserCreator


class PasswordLessUserCreationForm(forms.ModelForm):
    email = forms.CharField(label=_("Email"))
    first_name = forms.CharField(label=_("first name"), required=False)
    last_name = forms.CharField(label=_("last name"), required=False)

    class Meta:
        model = Student
        fields = [
            "email",
            "first_name",
            "last_name",
        ]

    def save_m2m(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        pass

    def save(self, commit: bool = True) -> User:
        return UserCreator(name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}", email=self.cleaned_data["email"])()


@admin.register(Student)
class StudentAdmin(ModelAdmin):
    """Basic admin for students"""

    add_form = PasswordLessUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "fields": ["email", "first_name", "last_name"],
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "gender", "tags")
    fieldsets = (
        (None, {"fields": ("username",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "gender")}),
        (_("Name in english"), {"fields": ("first_name_en", "last_name_en")}),
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "order__study__course",
    )
    list_editable = ("gender",)
