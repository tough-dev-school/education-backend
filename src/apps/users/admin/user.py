from django.contrib.auth.admin import UserAdmin as StockUserAdmin

from core.admin import admin
from apps.users.models import User


@admin.register(User)
class UserAdmin(StockUserAdmin):
    """Register stock django form to use it for user administrations"""
