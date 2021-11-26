from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from diplomas.models import Diploma, DiplomaTemplate


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
        'regenerate',
    ]

    readonly_fields = ['slug', 'course', 'student']

    @admin.display(description=_('Student'), ordering='study__student')
    def student(self, diploma):
        return diploma.study.student

    @admin.display(description=_('Course'), ordering='study__course')
    def course(self, diploma):
        return diploma.study.course

    @admin.action(description=_('Send diploma to student'))
    def send_to_student(self, request, queryset):
        for diploma in queryset.iterator():
            diploma.send_to_student()

        self.message_user(request, f'Diplomas sent to {queryset.count()} students')


@admin.register(DiplomaTemplate)
class DiplomaTemplateAdmin(ModelAdmin):
    fields = list_display = [
        'course',
        'language',
        'slug',
    ]

    list_editable = [
        'slug',
        'language',
    ]
