import datetime
from celery import group
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from diplomas.models import Diploma, DiplomaTemplate
from orders import tasks


@admin.register(Diploma)
class DiplomaAdmin(ModelAdmin):
    list_display = [
        'date',
        'student',
        'course',
        'language',
        'homework_accepted',
    ]
    fields = [
        'slug',
        'student',
        'study',
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
    list_select_related = ['study', 'study__student', 'study__course']
    raw_id_fields = ['study']

    @admin.display(description=_('Student'), ordering='study__student')
    def student(self, diploma: Diploma):
        return diploma.study.student

    @admin.display(description=_('Course'), ordering='study__course')
    def course(self, diploma: Diploma):
        return diploma.study.course

    @admin.display(description=_('Homework'), ordering='study__homework_accepted', boolean=True)
    def homework_accepted(self, diploma: Diploma) -> bool:
        return diploma.study.homework_accepted

    @admin.display(description=_('Date'), ordering='created')
    def date(self, diploma: Diploma) -> datetime.datetime:
        return diploma.modified or diploma.created

    @admin.action(description=_('Send diploma to student'))
    def send_to_student(self, request, queryset):
        for diploma in queryset.iterator():
            diploma.send_to_student()

        self.message_user(request, f'Diplomas sent to {queryset.count()} students')

    @admin.action(description=_('Regenerate diploma'))
    def regenerate(self, request, queryset):
        order_ids = queryset.values_list('study__order_id', flat=True).distinct()

        generate_diplams = group([tasks.generate_diploma.s(order_id=order_id) for order_id in order_ids])
        generate_diplams.skew(step=2).apply_async()

        self.message_user(request, f'Started generation of {len(order_ids)} diplomas')


@admin.register(DiplomaTemplate)
class DiplomaTemplateAdmin(ModelAdmin):
    fields = list_display = [
        'course',
        'language',
        'slug',
        'homework_accepted',
    ]

    list_editable = [
        'slug',
        'language',
        'homework_accepted',
    ]
