from django.utils.translation import gettext_lazy as _

from app.admin import ModelAdmin, admin
from products.models import Bundle


@admin.register(Bundle)
class BundleAdmin(ModelAdmin):
    list_display = [
        'id',
        'slug',
        'name',
    ]
    list_display_links = [
        'id',
        'slug',
    ]
    fieldsets = [
        (_('Name'), {'fields': [
            'name',
            'slug',
            'name_receipt',
            'full_name',
            'group',
        ]}),
        (_('Price'), {'fields': [
            'price',
            'old_price',
        ]}),
        (_('Items'), {'fields': [
            'records',
        ]}),
    ]

    prepopulated_fields = {
        'slug': ['name'],
    }
