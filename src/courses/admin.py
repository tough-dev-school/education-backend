from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, StackedInline, admin
from courses.models import Course, Record


class RecordAdmin(StackedInline):
    model = Record

    readonly_fields = [
        'downloadable',
    ]

    fieldsets = [
        (_('Name'), {'fields': [
            'name',
            'name_receipt',
            'full_name',
            'template_id',
        ]}),
        (_('Access'), {'fields': [
            'downloadable',
            's3_object_id',
        ]}),
    ]

    extra = 0

    def downloadable(self, obj):
        if obj is None or obj.s3_object_id is None or not len(obj.s3_object_id):
            return '—'

        return format_html('<a href="{}">Копировать</a>', obj.get_url())

    downloadable.short_description = _('Downloadable link')


@admin.register(Course)
class CourseAdmin(ModelAdmin):
    fieldsets = [
        (_('Name'), {'fields': [
            'name',
            'name_genitive',
            'name_receipt',
            'full_name',
        ]}),
        (_('Access'), {'fields': [
            'slug',
            'clickmeeting_room_url',
        ]}),
    ]

    list_display = [
        'id',
        'name',
        'slug',
    ]

    prepopulated_fields = {
        'slug': ['name'],
    }
    inlines = [
        RecordAdmin,
    ]
