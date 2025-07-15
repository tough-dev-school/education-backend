from typing import Any

from django import forms
from django.contrib.auth.forms import UserChangeForm as _UserChangeForm
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.users.models import AdminUserProxy, User
from core.admin import ModelForm


class PasswordlessUserCreationForm(ModelForm):
    email = forms.CharField(label=_("Email"))
    first_name = forms.CharField(label=_("first name"), required=False)
    last_name = forms.CharField(label=_("last name"), required=False)

    class Meta:
        model = AdminUserProxy
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
        from apps.users.services import UserCreator

        return UserCreator(name=f"{self.cleaned_data['first_name']} {self.cleaned_data['last_name']}", email=self.cleaned_data["email"])()

    @staticmethod
    def _send_to_dashamail(user: User) -> None: ...


class UserChangeForm(_UserChangeForm):
    def clean_email(self) -> str:
        from apps.users.services import UserEmailChanger

        if self.initial["email"] != self.cleaned_data["email"]:
            if User.objects.exclude(pk=self.instance.pk).filter(Q(email=self.cleaned_data["email"]) | Q(username=self.cleaned_data["email"])).exists():
                raise ValidationError(_("User with such email or login already exists"))
            UserEmailChanger(user=self.instance, new_email=self.cleaned_data["email"])()

        return self.cleaned_data["email"]


__all__ = [
    "PasswordlessUserCreationForm",
    "UserChangeForm",
]
