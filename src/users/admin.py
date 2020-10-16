from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from app.admin import admin
from users.models import User

admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    pass
