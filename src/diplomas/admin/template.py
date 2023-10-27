from app.admin import admin
from app.admin import ModelAdmin
from diplomas.models import DiplomaTemplate


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
