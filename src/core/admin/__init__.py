from django.contrib import admin

from core.admin.model_admin import ModelAdmin
from core.admin.model_admin import StackedInline
from core.admin.model_admin import TabularInline

__all__ = [
    "admin",
    "ModelAdmin",
    "StackedInline",
    "TabularInline",
]
