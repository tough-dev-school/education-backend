from django.utils.translation import ugettext_lazy as _

from app.admin import ModelAdmin, action, admin
from app.admin.filters import BooleanFilter
from onetime.models import Token


class ActiveFilter(BooleanFilter):
    title = _('Is active')
    parameter_name = 'is_active'

    def t(self, request, queryset):
        return queryset.active()

    def f(self, request, queryset):
        return queryset.exclude(id__in=queryset.active().values('pk'))


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    list_display = [
        'token',
        'course',
        'expires',
    ]

    search_fields = [
        'token',
    ]

    list_filter = [
        ActiveFilter,
    ]

    actions = [
        'renew',
    ]

    def course(self, obj):
        return str(obj.record.course)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'record',
            'record__course',
        )

    @action(short_description=_('Renew'))
    def renew(self, request, queryset):
        """Action to renew token"""
        queryset.update(expires=None)
        self.message_user(request, f'{queryset.count()} tokens renewd')
