from django.contrib import admin

from core.admin.mixin import AppAdminMixin


class ModelAdmin(AppAdminMixin, admin.ModelAdmin):
    pass


class StackedInline(AppAdminMixin, admin.StackedInline):
    pass


class TabularInline(AppAdminMixin, admin.TabularInline):
    pass


__all__ = [
    "ModelAdmin",
    "StackedInline",
    "TabularInline",
    "admin",
]
