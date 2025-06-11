from apps.banking.models import CurrencyRate
from core.admin import ModelAdmin, admin


@admin.register(CurrencyRate)
class CurrencyRateAdmin(ModelAdmin):
    list_display = ["name", "rate"]
