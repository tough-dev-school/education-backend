from app.admin import ModelAdmin, admin
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

    def courses_list(self, obj=None):
        return ', '.join([course.name for course in obj.courses.all()])


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_filter = [
        'question',
        'question__courses',
    ]
    list_display = [
        'question',
        'author',
        'short_text',
    ]
    fields = [
        'created',
        'author',
        'text',
    ]
    readonly_fields = fields

    def short_text(self, obj=None):
        return str(obj)
