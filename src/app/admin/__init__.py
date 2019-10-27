from django.contrib import admin

from app.admin.model_admin import ModelAdmin, StackedInline, TabularInline

__all__ = [
    admin,
    StackedInline,
    TabularInline,
    ModelAdmin,
]
