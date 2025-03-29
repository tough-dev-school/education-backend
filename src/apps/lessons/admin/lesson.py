from apps.lessons.models import Lesson
from core.admin import ModelAdmin, admin


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    fields = [
        "name",
        "material",
        "question",
        "hidden",
    ]
    raw_id_fields = [
        "material",
        "question",
    ]
