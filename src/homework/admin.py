from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, action, admin, field
from app.admin.filters import BooleanFilter
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
    save_as = True

    def courses_list(self, obj=None):
        return ', '.join([course.name for course in obj.courses.all()])

    @action(short_description=_('Dispatch crosscheck'))
    def dispatch_crosscheck(self, request, queryset):
        count = 0
        for question in queryset.iterator():
            count += question.dispatch_crosscheck()

        self.message_user(request, f'{count} users will check {queryset.count()} questions')


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
        'text',
    ]
    readonly_fields = fields

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
    def course(self, obj=None):
        course = obj.get_purchased_course()
        if course is None:
            return '—'

        return str(course)

    @field(short_description=_('Crosschecking people'), admin_order_field='crosscheck_count')
    def crosscheck_count(self, obj=None):
        return obj.crosscheck_count or '—'

    @mark_safe
    @field(short_description=_('Author'), admin_order_field='auhor')
    def _author(self, obj=None):
        author_url = reverse('admin:users_user_change', args=[obj.author_id])
        return f'<a href="{author_url}">{obj.author}</a>'
