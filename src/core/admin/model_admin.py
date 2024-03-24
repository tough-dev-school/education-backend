from django.contrib import admin

from core.admin.mixin import AppAdminMixin


class ModelAdmin(AppAdminMixin, admin.ModelAdmin):  # type: ignore
    pass


class StackedInline(AppAdminMixin, admin.StackedInline):  # type: ignore[misc]
    pass


class TabularInline(AppAdminMixin, admin.TabularInline):  # type: ignore[misc]
    pass


__all__ = [
    "admin",
    "ModelAdmin",
    "StackedInline",
    "TabularInline",
]
