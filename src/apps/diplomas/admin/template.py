from apps.diplomas.models import DiplomaTemplate
from core.admin import admin
from core.admin import ModelAdmin


@admin.register(DiplomaTemplate)
class DiplomaTemplateAdmin(ModelAdmin):
    fields = list_display = (
        "course",
        "language",
        "slug",
        "homework_accepted",
    )

    list_editable = [
        "slug",
        "language",
        "homework_accepted",
    ]
