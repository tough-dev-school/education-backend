from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, action, admin, field
from diplomas.models import Diploma


@admin.register(Diploma)
class DiplomaAdmin(ModelAdmin):
    list_display = [
        'student',
        'course',
    ]
    fields = [
        'slug',
        'student',
        'course',
        'language',
        'image',
    ]
    list_filter = [
        'language',
        'study__course',
    ]

    search_fields = [
        'study__student__first_name',
        'study__student__last_name',
        'study__student__email',
    ]
    actions = [
        'send_to_student',
    ]

    readonly_fields = ['slug', 'course', 'student']

    @field(short_description=_('Student'), admin_order_field='study__student')
    def student(self, diploma):
        return diploma.study.student

    @field(short_description=_('Course'), admin_order_field='study__course')
    def course(self, diploma):
        return diploma.study.course

    @action(short_description=_('Send diploma to student'))
    def send_to_student(self, request, queryset):
        for diploma in queryset.iterator():
            diploma.send_to_student()

        self.message_user(request, f'Diplomas sent to {queryset.count()} students')
