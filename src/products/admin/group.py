from app.admin import ModelAdmin, admin
from products.models import Group


@admin.register(Group)
class GroupAdmin(ModelAdmin):
    list_display = ['id', 'name']
    list_editable = ['name']
