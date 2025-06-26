from django.contrib.auth.admin import UserAdmin as StockUserAdmin

from apps.users.models import User
from core.admin import admin


@admin.register(User)
class UserAdmin(StockUserAdmin):
    """Register stock django form to use it for user administrations"""

    search_fields = ("username", "first_name", "last_name", "first_name_en", "last_name_en", "email")
