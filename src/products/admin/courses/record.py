from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from app.admin import StackedInline, admin
from products.models import Record


class RecordAdmin(StackedInline):
    model = Record

    readonly_fields = [
        'downloadable',
    ]

    fieldsets = [
        (
            _('Name'),
            {
                'fields': [
                    'name',
                    'name_receipt',
                    'full_name',
                    'group',
                    'template_id',
                ],
            },
        ),
        (
            _('Price'),
            {
                'fields': [
                    'price',
                    'old_price',
                ],
            },
        ),
        (
            _('Access'),
            {
                'fields': [
                    'slug',
                    'downloadable',
                    's3_object_id',
                ],
            },
        ),
    ]

    extra = 0

    @admin.display(description=_('Downloadable link'))
    def downloadable(self, obj):
        if obj is None or obj.s3_object_id is None or not len(obj.s3_object_id):
            return '—'

        return format_html('<a href="{}">Копировать</a>', obj.get_url())
