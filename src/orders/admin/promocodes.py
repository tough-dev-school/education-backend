from app.admin import ModelAdmin, admin
from orders.models import PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(ModelAdmin):
    list_display = [
        'id',
        'name',
        'active',
    ]

    list_editable = [
        'name',
        'active',
    ]
