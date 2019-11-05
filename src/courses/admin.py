from app.admin import ModelAdmin, StackedInline, admin
from courses.models import Course, Record


class RecordAdmin(StackedInline):
    model = Record

    fields = [
        'name',
        'slug',
        's3_object_id',
    ]

    display_fields = fields
    prepopulated_fields = {'slug': ('name',)}
    extra = 0


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fields = [
        'name',
        'name_genitive',
        'slug',
    ]
    display_fields = fields
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        RecordAdmin,
    ]
