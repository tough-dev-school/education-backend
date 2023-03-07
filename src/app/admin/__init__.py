from django.contrib import admin

from app.admin.model_admin import ModelAdmin
from app.admin.model_admin import StackedInline
from app.admin.model_admin import TabularInline

__all__ = [
    "admin",
    "ModelAdmin",
    "StackedInline",
    "TabularInline",
]
