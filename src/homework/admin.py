from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin, field
from app.admin.filters import BooleanFilter
from homework import tasks
from homework.models import Answer, AnswerCrossCheck, Question


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
            tasks.disptach_crosscheck.delay(question_id=question.id)

        self.message_user(request, f'Crosscheck dispatched for {queryset.count()} questions')


class IsRootFilter(BooleanFilter):
    title = _('Is root answer')
    parameter_name = 'is_root'

    def t(self, request, queryset):
        return queryset.filter(parent__isnull=True)

    def f(self, request, queryset):
        return queryset.filter(parent__isnull=False)


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    list_filter = [
        IsRootFilter,
        'question',
        'question__courses',
    ]
    list_display = [
        'created',
        'question',
        'course',
        '_author',
        'do_not_crosscheck',
        'crosscheck_count',
    ]
    fields = [
        'created',
        'author',
        'parent',
        'text',
    ]
    readonly_fields = [
        'created',
        'author',
        'text',
    ]
    raw_id_fields = [
        'parent',
    ]

    list_editable = [
        'do_not_crosscheck',
    ]

    search_fields = [
        'author__first_name',
        'author__last_name',
        'author__email',
        'text',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).with_crosscheck_count() \
            .select_related('author', 'question')

    @field(short_description=_('Course'))
    def course(self, obj):
        course = obj.get_purchased_course()
        if course is None:
            return '—'

        return str(course)

    @field(short_description=_('Crosschecking people'), admin_order_field='crosscheck_count')
    def crosscheck_count(self, obj):
        return obj.crosscheck_count or '—'

    @mark_safe
    @field(short_description=_('Author'), admin_order_field='author')
    def _author(self, obj):
        author_url = reverse('admin:users_student_change', args=[obj.author_id])
        return f'<a href="{author_url}">{obj.author}</a>'


@admin.register(AnswerCrossCheck)
class AnswerCrossCheckAdmin(ModelAdmin):
    fields = [
        'course',
        'question',
        'checker',
        'author',
        'view',
        'checked',
    ]
    list_display = fields
    readonly_fields = [
        'question',
        'course',
        'checked',
        'author',
        'view',
    ]
    list_filter = [
        'answer__question',
        'answer__question__courses',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('answer', 'answer__question', 'answer__author')

    @field(short_description=_('Course'))
    def course(self, obj):
        course = obj.answer.get_purchased_course()
        if course is None:
            return '—'

        return str(course)

    @field(short_description=_('Question'), admin_order_field='answer__question')
    def question(self, obj):
        return str(obj.answer.question)

    @field(short_description=_('Author'), admin_order_field='answer__author')
    def author(self, obj):
        return str(obj.answer.author)

    @field(short_description=_('View'))
    @mark_safe
    def view(self, obj):
        return f'<a href={obj.answer.get_absolute_url()}>Смотреть на сайте</a>'

    @field(short_description=_('Is checked'), boolean=True)
    def checked(self, obj):
        return obj.is_checked()
