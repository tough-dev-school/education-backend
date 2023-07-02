from dataclasses import dataclass

from django.utils import timezone

from app.services import BaseService
from orders.models import Order


@dataclass
class OrderUnpaidSetter(BaseService):
    """Mark order as not paid"""

    order: Order

    def __post_init__(self) -> None:
        self.was_paid_before_service_call = self.order.paid is not None

    def act(self) -> None:
        self.mark_order_as_not_paid()
        self.unship()

    def mark_order_as_not_paid(self) -> None:
        self.order.paid = None
        if self.was_paid_before_service_call:  # log unpayment date only if order has already been paid
            self.order.unpaid = timezone.now()

        self.order.save()

    def unship(self) -> None:
        if self.was_paid_before_service_call and self.order.item is not None:
            self.order.unship()
