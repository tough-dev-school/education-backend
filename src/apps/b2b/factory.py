from decimal import Decimal
from typing import Any

from apps.b2b.models import Customer, Deal
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
    student_count: int | None = 0,
    **kwargs: dict[str, Any],
) -> Deal:
    customer = self.mixer.blend("b2b.Customer") if customer is None else customer
    author = self.mixer.blend("users.User") if author is None else author
    course = self.course() if course is None else course
    price = price if price is not None else Decimal(self.price())

    deal = Deal.objects.create(
        customer=customer,
        course=course,
        price=price,
        author=author,
        **kwargs,
    )

    for _ in range(student_count or 0):
        deal.students.create(user=self.mixer.blend("users.User"))

    return deal
