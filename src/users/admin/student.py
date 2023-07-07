from typing import Any

from rest_framework.request import Request

from django import forms
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin
from users.models import Student
from users.models import User
from users.services import UserCreator


class StudentTagsFilter(admin.SimpleListFilter):
    """This is a tag filter based on the values
    from a model's `tags` ArrayField."""

    title = _("Tags")
    parameter_name = "tags"

    def lookups(self, request: Request, model_admin: ModelAdmin) -> list[tuple[str, str]]:
        tags = Student.objects.values_list(self.parameter_name, flat=True).distinct()
        tags = [(tag, tag) for sublist in tags for tag in sublist if tag]  # type: ignore
        return sorted(set(tags))

    def queryset(self, request: Request, queryset: QuerySet) -> QuerySet:
        """
        When user clicks on a filter, this method gets called.
        The provided queryset with be a queryset of Items, so we need to
        filter that based on the clicked keyword.
        """

        lookup_value = self.value()
        if lookup_value:
            return queryset.filter(tags__contains=[lookup_value])


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
        (_("Tags"), {"fields": ("tags",)}),
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "order__study__course", StudentTagsFilter)
    list_editable = ("gender",)
