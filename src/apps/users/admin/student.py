from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.dashamail.tasks import update_subscription as update_dashamail_subscription
from apps.users.models import Student, User
from apps.users.services import UserCreator
from core.admin import ModelAdmin, admin


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
        user = self._create_user()
        self._send_to_dashamail(user)

        return user

    def _create_user(self) -> User:
        return UserCreator(name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}", email=self.cleaned_data["email"])()

    @staticmethod
    def _send_to_dashamail(user: User) -> None:
        update_dashamail_subscription.apply_async(
            kwargs=dict(student_id=user.id),
            countdown=5,
        )


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
