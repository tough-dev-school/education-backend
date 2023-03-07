from django.contrib.auth.admin import UserAdmin as StockUserAdmin

from app.admin import admin
from users.models import User


@admin.register(User)
class UserAdmin(StockUserAdmin):
    """Register stock django form to use it for user administrations"""
