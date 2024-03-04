from collections.abc import Generator
from typing import TYPE_CHECKING, Any

from django.utils.translation import gettext_lazy as _

from apps.products.models.base import Shippable
from core.models import models

if TYPE_CHECKING:
    from apps.orders.models import Order
    from apps.users.models import User


class Bundle(Shippable):
    records = models.ManyToManyField("products.Record")
    courses = models.ManyToManyField("products.Course")

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Bundle")
        verbose_name_plural = _("Bundles")
        db_table = "courses_bundle"

    def iterate_bundled_items(self) -> Generator[Shippable, None, None]:
        yield from self.records.iterator()
        yield from self.courses.iterator()

    def ship(self, *args: "User | Order", **kwargs: "User | Order") -> None:
        for item in self.iterate_bundled_items():
            item.ship(*args, **kwargs)  # type: ignore

    def unship(self, *args: "Order", **kwargs: "Order") -> None:
        for item in self.iterate_bundled_items():
            item.unship(*args, **kwargs)

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Deprecated model")
