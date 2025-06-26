from django.utils.translation import gettext_lazy as _

from apps.users.admin.user.forms import PasswordlessUserCreationForm
from apps.users.models import AdminUserProxy
from core.admin import ModelAdmin, admin


@admin.register(AdminUserProxy)
class UserAdmin(ModelAdmin):
    """Basic admin for students"""

    add_form = PasswordlessUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "fields": ["email", "first_name", "last_name"],
            },
        ),
    )
    list_display = ("email", "first_name", "last_name", "gender")
    search_fields = ("username", "first_name", "last_name", "first_name_en", "last_name_en", "email")
    fieldsets = (
        (None, {"fields": ("username",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "gender")}),
        (_("Name in english"), {"fields": ("first_name_en", "last_name_en")}),
        (_("Marketing"), {"fields": ("tags",)}),
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "groups",
    )
    readonly_fields = [
        "tags",
    ]


__all__ = [
    "UserAdmin",
]
