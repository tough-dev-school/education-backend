from django.contrib import admin

from app.admin.decorators import action, field
from app.admin.model_admin import ModelAdmin, StackedInline, TabularInline

__all__ = [
    action,
    admin,
    field,
    ModelAdmin,
    StackedInline,
    TabularInline,
]
