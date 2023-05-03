from django.utils.translation import gettext_lazy as _

from app.admin import admin


@admin.action(description=_("Deactivate selected promo codes"))
def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)
