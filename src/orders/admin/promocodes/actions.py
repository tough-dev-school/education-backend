from app.admin import admin
from django.utils.translation import gettext_lazy as _


@admin.action(description=_('Deactivate selected promo codes'))
def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)
