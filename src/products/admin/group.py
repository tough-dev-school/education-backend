from app.admin import admin
from app.admin import ModelAdmin
from products.models import Group


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ["id", "name"]
    list_editable = ["name"]
