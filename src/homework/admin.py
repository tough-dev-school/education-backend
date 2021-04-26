from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, action, admin, field
from homework.models import Answer, Question


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = [
        'name',
        'courses_list',
    ]
    fields = [
        'courses',
        'name',
        'text',
    ]
    actions = [
        'dispatch_crosscheck',
    ]

    def courses_list(self, obj=None):
        return ', '.join([course.name for course in obj.courses.all()])

    @action(short_description=_('Dispatch crosscheck'))
    def dispatch_crosscheck(self, request, queryset):
        count = 0
        for question in queryset.iterator():
            count += question.dispatch_crosscheck()

        self.message_user(request, f'{count} users will check {queryset.count()} questions')


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_filter = [
        'question',
        'question__courses',
    ]
    list_display = [
        'question',
        'course',
        'author',
        'do_not_crosscheck',
        'short_text',
    ]
    fields = [
        'created',
        'author',
        'text',
    ]
    readonly_fields = fields

    list_editable = [
        'do_not_crosscheck',
    ]

    @field(short_description=_('Text'))
    def short_text(self, obj=None):
        return str(obj)

    @field(short_description=_('Course'))
    def course(self, obj=None):
        course = obj.get_purchased_course()
        if course is None:
            return '—'

        return str(course)
