from apps.dashamail.directcrm.events.base import Event as DirectCRMEvent
from apps.orders.models import Order


class OrderPaid(DirectCRMEvent):
    name = "OrderPaid"

    def __init__(self, order: Order) -> None:
        self.order = order

    def to_json(self) -> dict:
        return {
            "customer": {
                "email": self.order.user.email,
            },
            "order": {
                "orderId": self.order.slug,
                "totalPrice": self.format_price(self.order.price),
                "status": "finished",
                "lines": [
                    {
                        "productId": self.order.course.slug,
                        "quantity": 1,
                        "price": self.format_price(self.order.price),
                    }
                ],
            },
        }
