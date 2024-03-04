from dataclasses import dataclass

from django.utils.functional import cached_property

from apps.orders.models import Order
from apps.products.models import Course
from core.services import BaseService


@dataclass
class OrderCourseChanger(BaseService):
    order: Order
    course: Course

    def act(self) -> None:
        if self.was_shipped:
            self.order.unship()

        self.order.set_item(self.course)
        self.order.save(update_fields=["course", "modified"])

        if self.was_shipped:
            self.order.ship()

    @cached_property
    def was_shipped(self) -> bool:
        return self.order.shipped is not None
