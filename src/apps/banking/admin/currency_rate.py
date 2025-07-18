from apps.banking.models import Currency
from core.admin import ModelAdmin, admin


@admin.register(Currency)
class CurrencyRateAdmin(ModelAdmin):
    list_display = ["name", "rate"]
