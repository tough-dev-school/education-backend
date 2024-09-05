from apps.notion.models import MaterialFile
from core.admin import ModelAdmin, admin


@admin.register(MaterialFile)
class NotionMaterialFileAdmin(ModelAdmin): ...
