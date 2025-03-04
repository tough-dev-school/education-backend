from dataclasses import dataclass
from decimal import Decimal

from apps.b2b.models import Customer, Deal
from apps.products.models import Course
from core.current_user import get_current_user
from core.services import BaseService


@dataclass
class DealCreator(BaseService):
    customer: Customer
    product: Course
    price: Decimal
    comment: str | None = ""

    def act(self) -> Deal:
        return self.create()

    def create(self) -> Deal:
        author = get_current_user()
        if author is None:
            raise RuntimeError("User is not authenticated")

        return Deal.objects.create(
            customer=self.customer,
            product=self.product,
            author=author,
            price=self.price,
            comment=self.comment or "",
        )
