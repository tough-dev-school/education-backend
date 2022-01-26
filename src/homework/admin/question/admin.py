from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from homework import tasks
from homework.models import Question


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
    save_as = True

    def courses_list(self, obj):
        return ', '.join([course.name for course in obj.courses.all()])

    @admin.action(description=_('Dispatch crosscheck'))
    def dispatch_crosscheck(self, request, queryset):
        for question in queryset.iterator():
            tasks.disptach_crosscheck(question_id=question.id)

        self.message_user(request, f'Crosscheck dispatched for {queryset.count()} questions')
