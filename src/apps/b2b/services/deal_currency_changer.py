from dataclasses import dataclass
from typing import Callable

from django.contrib.admin.models import CHANGE

from apps.b2b.models import Deal
from apps.banking import currency
from core.current_user import get_current_user
from core.services import BaseService
from core.tasks import write_admin_log


@dataclass
class DealCurrencyChanger(BaseService):
    """Changes deal currency and currency rate on creation"""

    deal: Deal
    new_currency_code: str

    def act(self) -> None:
        self.deal.currency = self.new_currency_code.upper()
        self.deal.currency_rate_on_creation = currency.get_rate_or_default(self.new_currency_code)
        self.deal.save(update_fields=["currency", "currency_rate_on_creation", "modified"])

        self.write_auditlog()

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_currency_code,
        ]

    def write_auditlog(self) -> None:
        user = get_current_user()
        if user is None:
            raise RuntimeError("Cannot determine user")

        write_admin_log.delay(
            action_flag=CHANGE,
            change_message=f"Deal currency changed to {self.deal.currency}",
            model="b2b.Deal",
            object_id=self.deal.id,
            user_id=user.id,
        )

    def validate_currency_code(self) -> None:
        if currency.get_rate(self.new_currency_code.upper()) is None:
            raise TypeError("Non-existant currency code")
