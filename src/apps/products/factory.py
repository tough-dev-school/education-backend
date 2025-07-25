from decimal import Decimal

from apps.products.models import Course, Group
from core.helpers import random_string
from core.test.factory import FixtureFactory, register


@register
def course(
    self: FixtureFactory,
    name: str | None = None,
    tariff_name: str | None = None,
    slug: str | None = None,
    group: Group | None = None,
    price: Decimal | None = None,
    **kwargs: dict,
) -> Course:
    return Course.objects.create(
        product_name=name if name else self.faker.catch_phrase(),
        tariff_name=tariff_name if tariff_name else "",
        slug=slug if slug is not None else random_string(49),
        group=group if group is not None else self.group(),
        price=price if price is not None else self.price(),
        old_price=self.price(),
        **kwargs,
    )


@register
def group(self: FixtureFactory, slug: str | None = None, **kwargs: dict) -> Group:
    return self.mixer.blend(
        "products.Group",
        slug=slug if slug is not None else random_string(49),
        **kwargs,
    )
