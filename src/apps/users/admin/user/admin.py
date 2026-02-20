from django.utils.translation import gettext_lazy as _

from apps.users.admin.user import forms
from apps.users.models import AdminUserProxy
from core.admin import ModelAdmin, admin


@admin.register(AdminUserProxy)
class UserAdmin(ModelAdmin):
    """Replacement of django stock admin

    Takes care of emails uniqueness and our custom fields
    """

    add_form = forms.PasswordlessUserCreationForm
    form = forms.UserChangeForm
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
        (_("Rank"), {"fields": ("always_display_comments", "rank", "rank_label_color")}),
        (_("Marketing"), {"fields": ("tags",)}),
    )
    list_filter = (
        "is_staff",
        "is_superuser",
        "groups",
    )
    readonly_fields = [
        "tags",
        "username",
    ]

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/js/email_change_presave.js"]
        css = {
            "all": ["admin/css/email_change_presave.css"],
        }


__all__ = [
    "UserAdmin",
]
