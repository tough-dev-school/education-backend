from dataclasses import dataclass
from decimal import Decimal

from apps.b2b.models import Customer, Deal
from apps.banking import currency
from apps.products.models import Course
from core.current_user import get_current_user
from core.services import BaseService


@dataclass
class DealCreator(BaseService):
    customer: Customer
    course: Course
    price: Decimal
    currency: str | None = "RUB"
    comment: str | None = ""

    def act(self) -> Deal:
        return self.create()

    def create(self) -> Deal:
        author = get_current_user()
        if author is None:
            raise RuntimeError("User is not authenticated")

        return Deal.objects.create(
            customer=self.customer,
            course=self.course,
            author=author,
            price=self.price,
            currency=self.currency or "RUB",
            currency_rate_on_creation=currency.get_rate_or_default(self.currency or "RUB"),
            comment=self.comment or "",
        )
