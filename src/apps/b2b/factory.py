from decimal import Decimal
from typing import Any

from apps.b2b.models import Customer, Deal
from apps.banking import currency
from apps.products.models import Course
from apps.users.models import User
from core.test.factory import FixtureFactory, register


@register
def deal(
    self: FixtureFactory,
    customer: Customer | None = None,
    author: User | None = None,
    course: Course | None = None,
    price: Decimal | None = None,
    currency_code: str | None = None,
    student_count: int | None = 0,
    **kwargs: dict[str, Any],
) -> Deal:
    customer = self.mixer.blend("b2b.Customer") if customer is None else customer
    author = self.mixer.blend("users.User") if author is None else author
    course = self.course() if course is None else course
    price = price if price is not None else Decimal(self.price())
    currency_code = currency_code if currency_code is not None else "RUB"

    deal = Deal.objects.create(
        customer=customer,
        course=course,
        price=price,
        author=author,
        currency=currency_code,
        currency_rate_on_creation=currency.get_rate_or_default(currency_code),
        **kwargs,
    )

    for _ in range(student_count or 0):
        deal.students.create(user=self.mixer.blend("users.User"))

    return deal
