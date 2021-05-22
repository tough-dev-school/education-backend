from orders.models import Order


class OrderUnshipper:
    def __init__(self, order: Order):
        self.order = order

    def __call__(self):
        self.order.item.unship(order=self.order)

        self.mark_order_as_unpaid()
        self.mark_order_as_unshipped()

    def mark_order_as_unshipped(self):
        self.order.shipped = None
        self.order.save()

    def mark_order_as_unpaid(self):
        self.order.paid = None
        self.order.save()
