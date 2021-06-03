from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin, field
from diplomas.models import Diploma


@admin.register(Diploma)
class DiplomaAdmin(ModelAdmin):
    list_display = [
        'student',
        'course',
    ]
    fields = [
        'student',
        'course',
        'language',
        'image',
    ]

    readonly_fields = ['course', 'student']

    @field(short_description=_('Student'), admin_order_field='study__student')
    def student(self, diploma):
        return diploma.study.student

    @field(short_description=_('Course'), admin_order_field='study__course')
    def course(self, diploma):
        return diploma.study.course
