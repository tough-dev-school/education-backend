from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, TabularInline, admin
from courses.models import Course, Record


class RecordAdmin(TabularInline):
    model = Record

    fields = [
        'name',
        'name_receipt',
        'slug',
        's3_object_id',
        'downloadable',
    ]
    readonly_fields = [
        'downloadable',
    ]

    prepopulated_fields = {'slug': ('name',)}
    extra = 0

    def downloadable(self, obj):
        if obj is None or obj.s3_object_id is None or not len(obj.s3_object_id):
            return '—'

        return format_html('<a href="{}">Копировать</a>', obj.get_url())

    downloadable.short_description = _('Downloadable link')


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fields = [
        'name',
        'name_genitive',
        'name_genitive',
        'name_receipt',
        'slug',
    ]
    display_fields = fields
    prepopulated_fields = {
        'slug': ['name'],
    }
    inlines = [
        RecordAdmin,
    ]
